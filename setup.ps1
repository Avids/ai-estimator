$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
py -V:Astral/CPython3.11.15 -m venv .venv
if ($LASTEXITCODE -ne 0) { throw 'Install Python 3.12 first.' }
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed.' }
& .\.venv\Scripts\python.exe -m pytest -q
if ($LASTEXITCODE -ne 0) { throw 'Tests failed.' }
