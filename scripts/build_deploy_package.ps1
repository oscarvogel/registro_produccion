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

if (-not $SkipTests) {
    Run-Step "Backend tests" {
        Push-Location "backend"
        try {
            python -m pytest
        } finally {
            Pop-Location
        }
    }

    Run-Step "Frontend tests" {
        Push-Location "frontend"
        try {
            npm run test
        } finally {
            Pop-Location
        }
    }
}

Run-Step "Frontend build" {
    Push-Location "frontend"
    try {
        npm run build
    } finally {
        Pop-Location
    }
}

$OutputPath = Join-Path $RepoRoot $OutputDir
$StageRoot = Join-Path $OutputPath "stage"
$Stage = Join-Path $StageRoot "registro_produccion"
$PackageName = "registro_produccion_deploy_$ShortCommit.tar.gz"
$PackagePath = Join-Path $OutputPath $PackageName

if (Test-Path $StageRoot) {
    Remove-Item -LiteralPath $StageRoot -Recurse -Force
}

New-Item -ItemType Directory -Force -Path $Stage | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "backend") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "frontend") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "backend/app") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "frontend/dist") | Out-Null
New-Item -ItemType Directory -Force -Path (Join-Path $Stage "db_migrations") | Out-Null

Run-Step "Copiando backend/app" {
    Copy-Item -Recurse -Force "backend/app/*" (Join-Path $Stage "backend/app")
    Copy-Item -Force "backend/requirements.txt" (Join-Path $Stage "backend/requirements.txt")
}

Run-Step "Copiando frontend/dist" {
    Copy-Item -Recurse -Force "frontend/dist/*" (Join-Path $Stage "frontend/dist")
}

Run-Step "Copiando deploy script" {
    Copy-Item -Force "deploy_produccion_fg.sh" (Join-Path $Stage "deploy_produccion_fg.sh")
}

Run-Step "Copiando migraciones DB" {
    Copy-Item -Force -Path "db_migrations\*.sql" -Destination "$Stage\db_migrations\"
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
    } finally {
        Pop-Location
    }
}

$Hash = (Get-FileHash $PackagePath -Algorithm SHA256).Hash.ToLowerInvariant()
Write-Host "==> Paquete listo"
Write-Host "Path: $PackagePath"
Write-Host "Commit: $Commit"
Write-Host "SHA256: $Hash"
