$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot
try {
    docker compose up -d --build --wait
    if ($LASTEXITCODE -ne 0) { throw 'Docker Compose could not start the app.' }
    Write-Host 'http://localhost:8080/app/simple-order | Administrator / admin'
} finally {
    Pop-Location
}
