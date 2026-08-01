param(
    [string]$OutputDir = "dist_deploy",
    [switch]$AllowAnyBranch,
    [switch]$SkipTests
)

$ErrorActionPreference = "Stop"

function Run-Step {
    param(
        [string]$Name,
        [scriptblock]$Command
    )

    Write-Host "==> $Name"
    & $Command
}

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..")
Set-Location $RepoRoot

$Branch = (git branch --show-current).Trim()
$Commit = (git rev-parse HEAD).Trim()
$ShortCommit = (git rev-parse --short HEAD).Trim()

if (-not $AllowAnyBranch -and $Branch -ne "main") {
    throw "La rama actual es '$Branch'. Usar main o pasar -AllowAnyBranch."
}

Run-Step "Actualizando referencias remotas" {
    git fetch origin --prune
}

$OriginMain = (git rev-parse origin/main).Trim()
if (-not $AllowAnyBranch -and $Commit -ne $OriginMain) {
    throw "HEAD ($Commit) no coincide con origin/main ($OriginMain). No genero paquete viejo."
}

$TrackedChanges = (git status --porcelain --untracked-files=no)
if ($TrackedChanges) {
    throw "Hay cambios trackeados sin commitear. Commit/revert antes de empaquetar."
}

$OutputPath = Join-Path $RepoRoot $OutputDir
$StageRoot = Join-Path $OutputPath "stage"
$Stage = Join-Path $StageRoot "registro_produccion"
$PackageName = "registro_produccion_deploy_$ShortCommit.tar.gz"
$PackagePath = Join-Path $OutputPath $PackageName
$TempRoot = Join-Path ([System.IO.Path]::GetTempPath()) (
    "registro_produccion_package_" + [guid]::NewGuid().ToString("N")
)
$CleanSource = Join-Path $TempRoot "source"
$SourceArchive = Join-Path $TempRoot "source.tar"

try {
    New-Item -ItemType Directory -Force -Path $CleanSource | Out-Null

    Run-Step "Materializando el commit $Commit" {
        git archive --format=tar --output=$SourceArchive $Commit
        if ($LASTEXITCODE -ne 0) {
            throw "git archive fallo con codigo $LASTEXITCODE."
        }
        tar -xf $SourceArchive -C $CleanSource
        if ($LASTEXITCODE -ne 0) {
            throw "No se pudo extraer el commit materializado."
        }
    }

    Run-Step "Instalando dependencias frontend desde lockfile" {
        Push-Location (Join-Path $CleanSource "frontend")
        try {
            npm ci
            if ($LASTEXITCODE -ne 0) {
                throw "npm ci fallo con codigo $LASTEXITCODE."
            }
        } finally {
            Pop-Location
        }
    }

    if (-not $SkipTests) {
        Run-Step "Backend tests" {
            Push-Location (Join-Path $CleanSource "backend")
            try {
                python -m pytest
                if ($LASTEXITCODE -ne 0) {
                    throw "Backend tests fallaron con codigo $LASTEXITCODE."
                }
            } finally {
                Pop-Location
            }
        }

        Run-Step "Frontend tests" {
            Push-Location (Join-Path $CleanSource "frontend")
            try {
                npm run test
                if ($LASTEXITCODE -ne 0) {
                    throw "Frontend tests fallaron con codigo $LASTEXITCODE."
                }
            } finally {
                Pop-Location
            }
        }
    }

    Run-Step "Frontend build" {
        Push-Location (Join-Path $CleanSource "frontend")
        try {
            npm run build
            if ($LASTEXITCODE -ne 0) {
                throw "Frontend build fallo con codigo $LASTEXITCODE."
            }
        } finally {
            Pop-Location
        }
    }

    if (Test-Path $StageRoot) {
        Remove-Item -LiteralPath $StageRoot -Recurse -Force
    }

    New-Item -ItemType Directory -Force -Path $Stage | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Stage "backend") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Stage "frontend") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Stage "backend/app") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Stage "frontend/dist") | Out-Null
    New-Item -ItemType Directory -Force -Path (Join-Path $Stage "db_migrations") | Out-Null

    Run-Step "Copiando backend/app desde el commit materializado" {
        Copy-Item -Recurse -Force -Path (Join-Path $CleanSource "backend/app/*") `
            -Destination (Join-Path $Stage "backend/app")
        Copy-Item -Force -Path (Join-Path $CleanSource "backend/requirements.txt") `
            -Destination (Join-Path $Stage "backend/requirements.txt")
    }

    Run-Step "Copiando frontend/dist desde el commit materializado" {
        Copy-Item -Recurse -Force -Path (Join-Path $CleanSource "frontend/dist/*") `
            -Destination (Join-Path $Stage "frontend/dist")
    }

    Run-Step "Copiando deploy script" {
        Copy-Item -Force -Path (Join-Path $CleanSource "deploy_produccion_fg.sh") `
            -Destination (Join-Path $Stage "deploy_produccion_fg.sh")
    }

    Run-Step "Copiando migraciones DB" {
        Copy-Item -Force -Path (Join-Path $CleanSource "db_migrations\*.sql") `
            -Destination "$Stage\db_migrations\"
    }

    $Manifest = @(
        "name=registro_produccion"
        "commit=$Commit"
        "short_commit=$ShortCommit"
        "branch=$Branch"
        "built_at=$((Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ"))"
    )
    $Manifest | Set-Content -Encoding UTF8 (Join-Path $Stage "RELEASE_MANIFEST.txt")

    $ForbiddenEnvFiles = @(
        "backend/.env",
        "frontend/.env"
    )

    foreach ($Forbidden in $ForbiddenEnvFiles) {
        if (Test-Path (Join-Path $Stage $Forbidden)) {
            throw "El staging contiene $Forbidden. No empaqueto secretos."
        }
    }

    Get-ChildItem -Path $Stage -Directory -Recurse -Force -Filter "__pycache__" |
        Remove-Item -Recurse -Force

    Run-Step "Generando paquete" {
        New-Item -ItemType Directory -Force -Path $OutputPath | Out-Null
        if (Test-Path $PackagePath) {
            Remove-Item -LiteralPath $PackagePath -Force
        }
        Push-Location $Stage
        try {
            tar -czf $PackagePath backend frontend db_migrations deploy_produccion_fg.sh RELEASE_MANIFEST.txt
            if ($LASTEXITCODE -ne 0) {
                throw "No se pudo generar el paquete."
            }
        } finally {
            Pop-Location
        }
    }

    $Hash = (Get-FileHash $PackagePath -Algorithm SHA256).Hash.ToLowerInvariant()
    Write-Host "==> Paquete listo"
    Write-Host "Path: $PackagePath"
    Write-Host "Commit: $Commit"
    Write-Host "SHA256: $Hash"
} finally {
    if (Test-Path $TempRoot) {
        Remove-Item -LiteralPath $TempRoot -Recurse -Force
    }
}
