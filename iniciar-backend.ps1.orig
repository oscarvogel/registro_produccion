param(
    [string]$HostAddress = "0.0.0.0",
    [int]$Port = 8000
)

$ErrorActionPreference = "Stop"

$backendPath = Join-Path $PSScriptRoot "backend"
if (-not (Test-Path $backendPath)) {
    Write-Error "No se encontró la carpeta backend en: $backendPath"
    exit 1
}

Push-Location $backendPath
try {
    uvicorn app.main:app --reload --host $HostAddress --port $Port
}
finally {
    Pop-Location
}
