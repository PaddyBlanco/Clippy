# Copies the program and the apps to the device and restarts it. Unchanged files are skipped.
#   .\tools\install.ps1            (finds the device by itself)
#   .\tools\install.ps1 -Port COM6
# Needs Python with mpremote:  python -m pip install mpremote
param(
    [string] $Port = "",
    [string] $Python = "python"
)
$root = Split-Path $PSScriptRoot
Set-Location $root

# The PC preview leaves compiled files behind; they do not belong on the device
Get-ChildItem -Recurse -Directory -Filter __pycache__ device, apps | Remove-Item -Recurse -Force

$mp = @("-m", "mpremote")
if ($Port) { $mp += @("connect", $Port) }
$mp += "resume"   # do not restart the device before copying

& $Python @mp cp device/boot.py device/main.py ":/flash/" + cp -r device/clippy device/res ":/flash/" + cp -r apps ":/flash/"
if ($LASTEXITCODE -ne 0) { Write-Error "Copying failed. Is the device connected? Press its reset button once and try again."; exit 1 }
if (Test-Path local/bg/bg.jpg) { & $Python @mp cp local/bg/bg.jpg ":/flash/bg.jpg" }   # background lives outside the repo
& $Python @mp reset
"Installed. The device restarts now."
