#!/usr/bin/env pwsh
# Engineering Onboarding Copilot - Demo Launcher (Windows / PowerShell).
# Native twin of demo.sh. Prints each command before running, pauses between
# sections. Run from the repo root:  pwsh -File demo.ps1   (or right-click > Run)
#
# Note: ErrorActionPreference stays 'Continue'. Section 1 runs `ob check` on the
# bad example, which exits non-zero BY DESIGN (it found violations) - the demo
# must keep going past it.
$ErrorActionPreference = 'Continue'

# Make `ob` available without requiring the caller to pre-activate the venv.
if (Test-Path ".venv\Scripts\Activate.ps1") {
    . ".venv\Scripts\Activate.ps1"
}
elseif (-not (Get-Command ob -ErrorAction SilentlyContinue)) {
    Write-Host "error: .venv not found and 'ob' is not on PATH." -ForegroundColor Red
    Write-Host "Run setup first, from the repo root:"
    Write-Host '  uv venv; .venv\Scripts\Activate.ps1; uv pip install -e ".[dev]"'
    exit 1
}

function Invoke-DemoCommand {
    param([Parameter(ValueFromRemainingArguments = $true)] [object[]] $Cmd)
    Write-Host ""
    Write-Host ('$ ' + ($Cmd -join ' ')) -ForegroundColor Cyan
    Write-Host "-----------------------------------------" -ForegroundColor DarkGray
    $exe = $Cmd[0]
    $rest = @()
    if ($Cmd.Length -gt 1) { $rest = $Cmd[1..($Cmd.Length - 1)] }
    & $exe @rest
    if ($LASTEXITCODE -ne 0) {
        Write-Host "(command exited with status $LASTEXITCODE - continuing demo)" -ForegroundColor DarkGray
    }
}

function Wait-Demo {
    Write-Host ""
    Read-Host "-- Press Enter to continue --" | Out-Null
}

function Write-Section {
    param([string] $Title)
    Write-Host ""
    Write-Host "===========================================" -ForegroundColor Green
    Write-Host "  $Title" -ForegroundColor Green
    Write-Host "===========================================" -ForegroundColor Green
    Wait-Demo
}

Write-Section "Section 1 - The Hook: Catch a Bad Contribution"
Invoke-DemoCommand ob check examples/bad-first-contrib
Wait-Demo

Write-Section "Section 2 - The Clean Path"
Invoke-DemoCommand ob check examples/safe-first-contrib
Wait-Demo
Invoke-DemoCommand ob scaffold --task "add adaptive histogram equalization helper"
Wait-Demo

Write-Section "Section 3 - Multi-Audience Briefs"
Invoke-DemoCommand ob brief --role engineer --workspace examples/safe-first-contrib
Wait-Demo
Invoke-DemoCommand ob brief --role pm --workspace examples/safe-first-contrib
Wait-Demo
Invoke-DemoCommand ob brief --role qa --workspace examples/safe-first-contrib
Wait-Demo
Invoke-DemoCommand ob brief --role devops --workspace examples/safe-first-contrib
Wait-Demo

Write-Section "Section 4 - Guardrails: Boundary Enforcement"
Invoke-DemoCommand ob scaffold --task "add helper to skimage/_vendored/"
Wait-Demo

Write-Section "Section 5 - CI: Same Checks, Production Path"
Write-Host "(Show .github/workflows/ci.yml and GitHub Actions summary)" -ForegroundColor DarkGray
Wait-Demo

Write-Section "Demo Complete"
Write-Host "All sections demonstrated successfully." -ForegroundColor Green
Write-Host ""
Write-Host "Next: closing slides (tradeoffs, extensibility, close)"
