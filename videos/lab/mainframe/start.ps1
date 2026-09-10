$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) { throw 'Run .\setup.ps1 first.' }
& '.\.venv\Scripts\python.exe' simulator.py --port 2323 --gateway http://127.0.0.1:3000
exit $LASTEXITCODE
