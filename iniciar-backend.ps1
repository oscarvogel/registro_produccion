param(
    [string]$VenvActivate = "h:\\venv\\produccion\\Scripts\\Activate.ps1",
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000,
    [switch]$NoReload
)

$ErrorActionPreference = 'Stop'

if (-not (Test-Path $VenvActivate)) {
    Write-Error "No se encontró el virtualenv en: $VenvActivate"
    exit 1
}

Write-Host "Activando virtualenv: $VenvActivate"
& $VenvActivate

$backendPath = Join-Path $PSScriptRoot 'backend'
if (-not (Test-Path $backendPath)) {
    Write-Error "No se encontró la carpeta backend en: $backendPath"
    exit 1
}

Push-Location $backendPath
try {
    # Ensure backend directory is in PYTHONPATH so uvicorn reloader can import the package
    $env:PYTHONPATH = $backendPath + [System.IO.Path]::PathSeparator + ($env:PYTHONPATH -ne $null ? $env:PYTHONPATH : '')

    $uvicornArgs = @('app.main:app')
    if (-not $NoReload) { $uvicornArgs += '--reload' }
    $uvicornArgs += '--host'; $uvicornArgs += $HostAddress
    $uvicornArgs += '--port'; $uvicornArgs += $Port.ToString()

    Write-Host "Ejecutando (cwd=$PWD): uvicorn $($uvicornArgs -join ' ')"
    & uvicorn @uvicornArgs
}
finally {
    Pop-Location
}
