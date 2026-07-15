# Publish LeadGen AI to PyPI
# Developed by Gyan Ranjan
#
# 1) Create account: https://pypi.org/account/register/
# 2) Enable 2FA, then create token: https://pypi.org/manage/account/token/
# 3) Run:
#      .\publish_pypi.ps1
#    or:
#      $env:PYPI_TOKEN = "pypi-..."
#      .\publish_pypi.ps1

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  LeadGen AI → PyPI" -ForegroundColor Cyan
Write-Host "  Developed by Gyan Ranjan" -ForegroundColor Magenta
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    python -m venv .venv
}
.\.venv\Scripts\pip install -q build twine

Write-Host "Building package..." -ForegroundColor Cyan
Remove-Item -Recurse -Force dist, build -ErrorAction SilentlyContinue
Get-ChildItem -Filter "*.egg-info" -Directory | Remove-Item -Recurse -Force -ErrorAction SilentlyContinue
.\.venv\Scripts\python -m build
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }

$token = $env:PYPI_TOKEN
if (-not $token) {
    Write-Host ""
    Write-Host "Paste your PyPI API token (starts with pypi-)." -ForegroundColor Yellow
    Write-Host "Create one at: https://pypi.org/manage/account/token/" -ForegroundColor DarkGray
    Write-Host "Token is hidden as you type / paste." -ForegroundColor DarkGray
    $secure = Read-Host "PYPI token" -AsSecureString
    $BSTR = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
    $token = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($BSTR)
}

if (-not $token -or -not $token.StartsWith("pypi-")) {
    Write-Host "Invalid token. It must start with 'pypi-'." -ForegroundColor Red
    exit 1
}

Write-Host "Uploading to PyPI..." -ForegroundColor Green
$env:TWINE_USERNAME = "__token__"
$env:TWINE_PASSWORD = $token
.\.venv\Scripts\twine upload dist/*

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "Published! Anyone can install with:" -ForegroundColor Green
    Write-Host "  pip install leadgen-ai" -ForegroundColor White
    Write-Host "  leadgen search `"dental clinics Mumbai`" -n 5" -ForegroundColor White
    Write-Host ""
    Write-Host "Package page: https://pypi.org/project/leadgen-ai/" -ForegroundColor Cyan
    Write-Host "Developed by Gyan Ranjan" -ForegroundColor Magenta
} else {
    Write-Host "Upload failed. Check token and package name." -ForegroundColor Red
    exit $LASTEXITCODE
}
