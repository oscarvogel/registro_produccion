<#
.SYNOPSIS
    Despliega registro_produccion a produccion (Coolify) con las etiquetas de version
    correctas y verifica que quedo todo arriba.

.DESCRIPTION
    El deploy real lo hace Coolify (build pack dockercompose) en el host fasa_189.
    Este script encadena los pasos que hay que hacer SIEMPRE juntos, porque Coolify
    tiene una trampa con las variables de version:

    - El compose declara `BUILD_COMMIT: ${SOURCE_COMMIT:-unknown}` y
      `BUILD_BRANCH: ${COOLIFY_BRANCH:-unknown}`.
    - Coolify materializa en la tabla de variables de la app toda variable referenciada
      con la forma `${VAR:-default}`, creando la fila CON EL VALOR POR DEFECTO.
      Por eso la app tiene `SOURCE_COMMIT=unknown` y `COOLIFY_BRANCH=unknown`, y
      Coolify las vuelve a crear en cada deploy.
    - Mientras esa fila exista, Coolify NO inyecta el SHA real (su codigo solo lo hace
      si la fila esta vacia), asi que `/api/health` sigue reportando `commit: unknown`.

    La unica forma de que el health diga la verdad es setear esas variables con el
    commit real ANTES de deployar. Eso es lo que hace este script.

    El token de la API de Coolify se lee de `$env:COOLIFY_TOKEN` o de
    `%USERPROFILE%\.coolify-token`. No hay credenciales en el repo.

.PARAMETER Commit
    SHA a desplegar. Por defecto, el de `origin/<Branch>`.

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\deploy_produccion_fg.ps1

.EXAMPLE
    powershell -ExecutionPolicy Bypass -File scripts\deploy_produccion_fg.ps1 -Commit 5eb79f4a6e6a765fe622c95658c043a80b71c3aa
#>
param(
    [string]$App = "4hcjxromkdmdylfjbw0fgvs4",
    [string]$Branch = "main",
    [string]$Commit = "",
    [string]$CoolifyUrl = "https://coolify.vogelconsultoria.com.ar",
    [string]$HealthUrl = "https://produccion.servinlgsm.com.ar",
    [string]$InduforUrl = "https://produccion.indufor.com.ar",
    [int]$TimeoutMinutes = 40,
    [switch]$SkipDeploy,
    [switch]$SkipVerify
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

function Get-CoolifyToken {
    if ($env:COOLIFY_TOKEN) {
        return $env:COOLIFY_TOKEN.Trim()
    }
    $TokenFile = Join-Path $env:USERPROFILE ".coolify-token"
    if (Test-Path $TokenFile) {
        return (Get-Content $TokenFile -Raw).Trim()
    }
    throw "No se encontro el token de Coolify. Setear COOLIFY_TOKEN o crear $TokenFile."
}

function Invoke-Coolify {
    param(
        [string]$Path,
        [string]$Method = "GET",
        $Body = $null
    )

    $Headers = @{ Authorization = "Bearer $script:Token" }
    $Params = @{
        Uri         = "$CoolifyUrl/api/v1$Path"
        Headers     = $Headers
        Method      = $Method
        TimeoutSec  = 120
    }
    if ($null -ne $Body) {
        $Params.Body = ($Body | ConvertTo-Json -Depth 6)
        $Params.ContentType = "application/json"
    }
    Invoke-RestMethod @Params
}

function Get-RemoteCommit {
    $Remote = git ls-remote origin "refs/heads/$Branch"
    if ($LASTEXITCODE -ne 0 -or -not $Remote) {
        throw "No se pudo resolver origin/$Branch."
    }
    return ($Remote -split "\s+")[0]
}

function Set-VersionVariables {
    param(
        [string]$Sha,
        [string]$BranchName
    )

    $Envs = Invoke-Coolify -Path "/applications/$App/envs"
    $Targets = @($Envs | Where-Object { $_.key -in @("SOURCE_COMMIT", "COOLIFY_BRANCH") })
    if ($Targets.Count -eq 0) {
        throw "La app de Coolify no tiene SOURCE_COMMIT ni COOLIFY_BRANCH. Revisar el setup."
    }

    foreach ($Env in $Targets) {
        $Value = if ($Env.key -eq "SOURCE_COMMIT") { $Sha } else { $BranchName }
        $Payload = @{
            key        = $Env.key
            value      = $Value
            is_preview = [bool]$Env.is_preview
        }
        Invoke-Coolify -Path "/applications/$App/envs" -Method "PATCH" -Body $Payload | Out-Null
        Write-Host ("    {0} (preview={1}) = {2}" -f $Env.key, $Env.is_preview, $Value)
    }
}

function Start-CoolifyDeploy {
    $Response = Invoke-Coolify -Path "/deploy" -Method "POST" -Body @{ uuid = $App; force = $true }
    return $Response.deployments[0].deployment_uuid
}

function Wait-CoolifyDeploy {
    param([string]$DeploymentUuid)

    $Deadline = (Get-Date).AddMinutes($TimeoutMinutes)
    $LastStatus = ""
    while ((Get-Date) -lt $Deadline) {
        $Deployment = Invoke-Coolify -Path "/deployments/$DeploymentUuid"
        if ($Deployment.status -ne $LastStatus) {
            Write-Host ("    status={0} commit={1}" -f $Deployment.status, $Deployment.commit)
            $LastStatus = $Deployment.status
        }
        if ($Deployment.status -in @("finished", "failed", "cancelled", "error")) {
            return $Deployment
        }
        Start-Sleep -Seconds 15
    }
    throw "El deploy $DeploymentUuid no termino en $TimeoutMinutes minutos."
}

function Get-BundleHash {
    param([string]$Url)

    # El contenedor del frontend puede reiniciar despues que el backend: el
    # index.html puede no estar disponible en el primer intento.
    for ($Try = 1; $Try -le 5; $Try++) {
        try {
            $Index = Invoke-WebRequest -Uri "$Url/" -UseBasicParsing -TimeoutSec 60
            if ($Index.Content -match "assets/index-([A-Za-z0-9_-]+)\.js") {
                return @{
                    Bundle       = "index-$($Matches[1]).js"
                    LastModified = $Index.Headers["Last-Modified"]
                }
            }
        } catch {
            Write-Host ("    (intento {0}: el frontend todavia no responde)" -f $Try)
        }
        Start-Sleep -Seconds 5
    }
    return @{ Bundle = "(no se pudo leer el index.html)"; LastModified = "" }
}

function Test-Instance {
    param(
        [string]$Url,
        [string]$ExpectedCommit,
        [string]$ExpectedBranch
    )

    $Health = Invoke-RestMethod -Uri "$Url/api/health" -TimeoutSec 60
    if ($Health.database -ne "ok") {
        throw "$Url responde con database=$($Health.database)."
    }
    if ($Health.commit -ne $ExpectedCommit) {
        throw "$Url reporta commit=$($Health.commit) y se esperaba $ExpectedCommit."
    }
    if ($Health.branch -ne $ExpectedBranch) {
        throw "$Url reporta branch=$($Health.branch) y se esperaba $ExpectedBranch."
    }

    $Frontend = Get-BundleHash -Url $Url
    Write-Host ("    {0} -> commit={1} branch={2} database={3} bundle={4} last-modified={5}" -f `
        $Url, $Health.commit, $Health.branch, $Health.database, $Frontend.Bundle, $Frontend.LastModified)
}

$script:Token = Get-CoolifyToken

if (-not $Commit) {
    $Commit = Get-RemoteCommit
}
if ($Commit -notmatch "^[0-9a-fA-F]{40}$") {
    throw "El commit '$Commit' no parece un SHA valido."
}
Write-Host "==> Commit a desplegar: $Commit ($Branch)"
Write-Host "    APP_VERSION sigue siendo el del env file del host (root): la referencia es commit."

Run-Step "Actualizando las variables de version en Coolify" {
    Set-VersionVariables -Sha $Commit -BranchName $Branch
}

if ($SkipDeploy) {
    Write-Host "==> -SkipDeploy: no se dispara el deploy."
} else {
    Run-Step "Disparando el deploy" {
        $script:DeploymentUuid = Start-CoolifyDeploy
        Write-Host "    deployment_uuid: $script:DeploymentUuid"
    }

    Run-Step "Esperando el deploy" {
        $Deployment = Wait-CoolifyDeploy -DeploymentUuid $script:DeploymentUuid
        if ($Deployment.status -ne "finished") {
            throw "El deploy termino con status=$($Deployment.status)."
        }
        if ($Deployment.commit -ne $Commit) {
            throw "Coolify desplego $($Deployment.commit) y se esperaba $Commit."
        }
    }
}

if ($SkipVerify) {
    Write-Host "==> -SkipVerify: no se verifica /api/health."
} else {
    Run-Step "Verificando las instancias" {
        Test-Instance -Url $HealthUrl -ExpectedCommit $Commit -ExpectedBranch $Branch
        Test-Instance -Url $InduforUrl -ExpectedCommit $Commit -ExpectedBranch $Branch
    }
}

Write-Host "==> Listo"
