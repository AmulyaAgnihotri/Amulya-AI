# ============================================================
#  run.ps1  —  PowerShell Launch Script for Amulya AI
# ============================================================

param(
    [switch]$Admin,
    [switch]$Logs
)

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path

# Colors for output
$Info = "Cyan"
$Success = "Green"
$Warning = "Yellow"
$Error_Color = "Red"

Write-Host "╔════════════════════════════════════════╗" -ForegroundColor $Info
Write-Host "║       Amulya AI - Voice Assistant      ║" -ForegroundColor $Info
Write-Host "╚════════════════════════════════════════╝" -ForegroundColor $Info
Write-Host ""

# Check if venv exists
if (-not (Test-Path "$ScriptDir\.venv_new\Scripts\python.exe")) {
    Write-Host "ERROR: Virtual environment not found!" -ForegroundColor $Error_Color
    Write-Host "Please run: python -m venv .venv_new" -ForegroundColor $Warning
    Write-Host "Then run: .venv_new\Scripts\pip install -r requirements.txt" -ForegroundColor $Warning
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if main.py exists
if (-not (Test-Path "$ScriptDir\main.py")) {
    Write-Host "ERROR: main.py not found!" -ForegroundColor $Error_Color
    Read-Host "Press Enter to exit"
    exit 1
}

# Show logs if requested
if ($Logs) {
    Write-Host "Recent logs:" -ForegroundColor $Info
    if (Test-Path "$ScriptDir\logs") {
        Get-ChildItem "$ScriptDir\logs" -File | Sort-Object LastWriteTime -Descending | Select-Object -First 5 | ForEach-Object {
            Write-Host "  - $($_.Name) ($('{0:N0}' -f $_.Length) bytes)" -ForegroundColor $Success
        }
    }
    Write-Host ""
}

Write-Host "Starting Amulya AI..." -ForegroundColor $Success
Write-Host "Say 'Hey Amulya' to activate the assistant" -ForegroundColor $Info
Write-Host ""

# Run the app
& "$ScriptDir\.venv_new\Scripts\python.exe" "$ScriptDir\main.py"

# Handle exit code
$exitCode = $LASTEXITCODE
if ($exitCode -ne 0) {
    Write-Host ""
    Write-Host "Application exited with error code: $exitCode" -ForegroundColor $Error_Color
    Write-Host "Check logs in the 'logs' folder for more details" -ForegroundColor $Warning
}
