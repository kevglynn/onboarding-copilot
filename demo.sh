#!/usr/bin/env bash
set -euo pipefail

# Engineering Onboarding Copilot — Demo Launcher
# Prints each command before executing. Pauses between sections.
# Usage: bash demo.sh

BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'

run() {
    echo ""
    echo -e "${CYAN}${BOLD}\$ $*${RESET}"
    echo -e "${DIM}─────────────────────────────────────────${RESET}"
    "$@"
}

pause() {
    echo ""
    echo -e "${DIM}── Press Enter to continue ──${RESET}"
    read -r
}

section() {
    echo ""
    echo ""
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${RESET}"
    echo -e "${GREEN}${BOLD}  $1${RESET}"
    echo -e "${GREEN}${BOLD}═══════════════════════════════════════════${RESET}"
    pause
}

section "Section 1 — The Hook: Catch a Bad Contribution"

run ob check examples/bad-first-contrib

pause

section "Section 2 — The Clean Path"

run ob check examples/safe-first-contrib

pause

run ob scaffold --task "add adaptive histogram equalization helper"

pause

section "Section 3 — Multi-Audience Briefs"

run ob brief --role engineer --workspace examples/safe-first-contrib

pause

run ob brief --role pm --workspace examples/safe-first-contrib

pause

run ob brief --role qa --workspace examples/safe-first-contrib

pause

run ob brief --role devops --workspace examples/safe-first-contrib

pause

section "Section 4 — Guardrails: Boundary Enforcement"

run ob scaffold --task "add helper to skimage/_vendored/"

pause

section "Section 5 — CI: Same Checks, Production Path"

echo -e "${DIM}(Show .github/workflows/ci.yml and GitHub Actions summary)${RESET}"

pause

section "Demo Complete"

echo -e "${GREEN}${BOLD}All sections demonstrated successfully.${RESET}"
echo ""
echo "Next: closing slides (tradeoffs, extensibility, close)"
