$ErrorActionPreference = 'Stop'
$url = 'http://localhost:8000'
$healthUrl = 'http://127.0.0.1:8000/api/method/ping'

& wsl -d Ubuntu -u root -- service mariadb start
if ($LASTEXITCODE -ne 0) { throw 'Cannot start MariaDB in Ubuntu WSL.' }

try {
    $ping = Invoke-RestMethod $healthUrl -TimeoutSec 5
    if ($ping.message -eq 'pong') {
        Write-Host "Frappe is running: $url/app/simple-order"
        return
    }
} catch { }

$logDirectory = Join-Path $PSScriptRoot '.cache'
New-Item -ItemType Directory -Force -Path $logDirectory | Out-Null
$windowsProject = $PSScriptRoot.Replace('\', '/')
$linuxProject = & wsl -d Ubuntu -- wslpath -a $windowsProject
if ($LASTEXITCODE -ne 0 -or -not $linuxProject) { throw 'Cannot resolve the project path in WSL.' }
$linuxProject = $linuxProject.Trim()

Start-Process -FilePath 'wsl.exe' -WindowStyle Hidden -ArgumentList @(
    '-d', 'Ubuntu', '--', 'bash', "$linuxProject/scripts/serve.sh"
) -RedirectStandardOutput (Join-Path $logDirectory 'bench.log') `
  -RedirectStandardError (Join-Path $logDirectory 'bench.error.log') | Out-Null

for ($attempt = 0; $attempt -lt 45; $attempt++) {
    Start-Sleep -Seconds 1
    try {
        $ping = Invoke-RestMethod $healthUrl -TimeoutSec 5
        if ($ping.message -eq 'pong') {
            Write-Host "Frappe is running: $url/app/simple-order"
            return
        }
    } catch { }
}

throw 'Frappe did not become ready. Check .cache/bench.log and .cache/bench.error.log.'
