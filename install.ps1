# Install LeadGen AI so you can type "leadgen" from ANY folder
# Developed by Gyan Ranjan
#
# Run once:
#   cd path\to\lead_agent
#   .\install.ps1

$ErrorActionPreference = "Stop"
$Root = $PSScriptRoot
$BinDir = Join-Path $env:USERPROFILE "bin"

Write-Host ""
Write-Host "  LeadGen AI - Installer" -ForegroundColor Cyan
Write-Host "  Developed by Gyan Ranjan" -ForegroundColor Magenta
Write-Host ""

# 1) Ensure venv + deps
$python = Join-Path $Root ".venv\Scripts\python.exe"
if (-not (Test-Path $python)) {
    Write-Host "Creating venv..." -ForegroundColor Cyan
    python -m venv (Join-Path $Root ".venv")
}
Write-Host "Installing dependencies..." -ForegroundColor Cyan
$pip = Join-Path $Root ".venv\Scripts\pip.exe"
& $pip install -q -r (Join-Path $Root "requirements.txt")

# 2) User bin folder + launchers
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

$cmdPath = Join-Path $BinDir "leadgen.cmd"
$batAlias = Join-Path $BinDir "lead_agent.cmd"
$ps1Path = Join-Path $BinDir "leadgen.ps1"

# CMD shim (works from cmd.exe and PowerShell)
$shimLines = @(
    "@echo off",
    "call `"$Root\leadgen.cmd`" %*"
)
$shimText = $shimLines -join "`r`n"
Set-Content -Path $cmdPath -Value $shimText -Encoding ASCII
Set-Content -Path $batAlias -Value $shimText -Encoding ASCII

# PowerShell helper
$ps1Lines = @(
    "# LeadGen AI launcher - Developed by Gyan Ranjan",
    "Set-Location -LiteralPath '$Root'",
    "& '$Root\leadgen.cmd' @args"
)
Set-Content -Path $ps1Path -Value ($ps1Lines -join "`r`n") -Encoding UTF8

# 3) Add %USERPROFILE%\bin to User PATH if missing
$userPath = [Environment]::GetEnvironmentVariable("Path", "User")
if (-not $userPath) { $userPath = "" }
$pathParts = @($userPath -split ";" | Where-Object { $_ -ne "" })
if ($pathParts -notcontains $BinDir) {
    if ($userPath.Trim().Length -gt 0) {
        $newPath = $userPath.TrimEnd(";") + ";" + $BinDir
    } else {
        $newPath = $BinDir
    }
    [Environment]::SetEnvironmentVariable("Path", $newPath, "User")
    $env:Path = $env:Path + ";" + $BinDir
    Write-Host "Added to PATH: $BinDir" -ForegroundColor Green
} else {
    if (($env:Path -split ";") -notcontains $BinDir) {
        $env:Path = $env:Path + ";" + $BinDir
    }
    Write-Host "PATH already includes: $BinDir" -ForegroundColor DarkGray
}

# 4) PowerShell profile aliases
$profilePath = $PROFILE
$profileDir = Split-Path -Parent $profilePath
if (-not (Test-Path $profileDir)) {
    New-Item -ItemType Directory -Force -Path $profileDir | Out-Null
}
if (-not (Test-Path $profilePath)) {
    New-Item -ItemType File -Force -Path $profilePath | Out-Null
    Set-Content -Path $profilePath -Value "" -Encoding UTF8
}

$aliasLines = @(
    "",
    "# >>> LeadGen AI (Gyan Ranjan) >>>",
    "function leadgen { & '$Root\leadgen.cmd' @args }",
    "function lead_agent { & '$Root\leadgen.cmd' @args }",
    "Set-Alias -Name lead -Value leadgen -ErrorAction SilentlyContinue",
    "# <<< LeadGen AI <<<",
    ""
)
$aliasBlock = $aliasLines -join "`r`n"

$existing = Get-Content $profilePath -Raw -ErrorAction SilentlyContinue
if (-not $existing) { $existing = "" }

if ($existing -match "LeadGen AI \(Gyan Ranjan\)") {
    $cleaned = [regex]::Replace(
        $existing,
        "(?s)# >>> LeadGen AI \(Gyan Ranjan\) >>>.*?# <<< LeadGen AI <<<\r?\n?",
        ""
    )
    Set-Content -Path $profilePath -Value ($cleaned.TrimEnd() + "`r`n" + $aliasBlock) -Encoding UTF8
    Write-Host "Updated leadgen aliases in PowerShell profile" -ForegroundColor Green
} else {
    Add-Content -Path $profilePath -Value $aliasBlock -Encoding UTF8
    Write-Host "Added leadgen / lead_agent aliases to PowerShell profile" -ForegroundColor Green
}

# Load aliases into current session
function global:leadgen { & "$Root\leadgen.cmd" @args }
function global:lead_agent { & "$Root\leadgen.cmd" @args }

Write-Host ""
Write-Host "Installed successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Use from ANY folder:" -ForegroundColor Yellow
Write-Host "  leadgen" -ForegroundColor White
Write-Host "  leadgen search `"dental clinics Mumbai`" -n 5" -ForegroundColor White
Write-Host "  lead_agent" -ForegroundColor White
Write-Host ""
Write-Host "If a NEW PowerShell window does not find leadgen, restart the terminal." -ForegroundColor DarkGray
Write-Host ""
Write-Host "Developed by Gyan Ranjan" -ForegroundColor Magenta
