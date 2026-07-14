# LeadGen AI — local runner
# Developed by Gyan Ranjan
#
# Usage:
#   .\run.ps1
#   .\run.ps1 -Keywords "dental clinics Mumbai"
#   .\run.ps1 -Keywords "HR SaaS startups USA" -Count 10 -Geo "United States"

param(
    [Parameter(Position = 0)]
    [string]$Keywords = "",
    [int]$Count = 8,
    [string]$Geo = "",
    [string]$Size = "",
    [int]$MinScore = 40
)

$ErrorActionPreference = "Stop"
Set-Location $PSScriptRoot

Write-Host ""
Write-Host "  LeadGen AI  v1.1" -ForegroundColor Cyan
Write-Host "  Search any keywords → get real sales leads" -ForegroundColor Gray
Write-Host "  Developed by Gyan Ranjan" -ForegroundColor Magenta
Write-Host ""

if (-not (Test-Path ".\.venv\Scripts\python.exe")) {
    Write-Host "Creating venv..." -ForegroundColor Cyan
    python -m venv .venv
}

Write-Host "Checking dependencies..." -ForegroundColor Cyan
.\.venv\Scripts\pip install -q -r requirements.txt

if (-not $env:XAI_API_KEY) {
    $authPath = Join-Path $env:USERPROFILE ".grok\auth.json"
    if (Test-Path $authPath) {
        $auth = Get-Content $authPath -Raw | ConvertFrom-Json
        $prop = $auth.PSObject.Properties | Select-Object -First 1
        if ($prop -and $prop.Value.key) {
            $env:XAI_API_KEY = $prop.Value.key
            Write-Host "Using Grok local auth token" -ForegroundColor DarkGray
        }
    }
}

if (-not $env:XAI_API_KEY -and (Test-Path ".\.env")) {
    Get-Content ".\.env" | ForEach-Object {
        if ($_ -match '^\s*XAI_API_KEY\s*=\s*(.+)\s*$') {
            $env:XAI_API_KEY = $Matches[1].Trim().Trim('"').Trim("'")
        }
    }
}

if (-not $env:XAI_API_KEY) {
    Write-Host "Missing XAI_API_KEY. Set it in .env or sign in to Grok." -ForegroundColor Red
    exit 1
}

if (-not $Keywords) {
    Write-Host "Enter any keywords to find leads (e.g. dental clinics Delhi, AI startups US)" -ForegroundColor Yellow
    $Keywords = Read-Host "Keywords"
    if (-not $Keywords) {
        Write-Host "No keywords entered." -ForegroundColor Red
        exit 1
    }
    $geoIn = Read-Host "Geo filter (optional)"
    if ($geoIn) { $Geo = $geoIn }
    $countIn = Read-Host "How many leads? [8]"
    if ($countIn) { $Count = [int]$countIn }
}

$argsList = @("search", $Keywords, "-n", "$Count", "--min-score", "$MinScore")
if ($Geo) { $argsList += @("--geo", $Geo) }
if ($Size) { $argsList += @("--size", $Size) }

Write-Host "Searching leads for: $Keywords" -ForegroundColor Green
& .\.venv\Scripts\python main.py @argsList

Write-Host "`nMerging all leads → output\all_leads.csv ..." -ForegroundColor Cyan
.\.venv\Scripts\python main.py merge-all

Write-Host "`nDone. Open: output\all_leads.csv" -ForegroundColor Green
Write-Host "Developed by Gyan Ranjan" -ForegroundColor Magenta
