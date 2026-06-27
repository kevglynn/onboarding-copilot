#!/usr/bin/env bash
# Note: intentionally NOT using `set -e`. Section 1 runs `ob check` on the bad
# example, which exits non-zero BY DESIGN (it found violations). Under `set -e`
# that would abort the whole demo after Section 1.
set -uo pipefail

# Engineering Onboarding Copilot — Demo Launcher
# Prints each command before executing. Pauses between sections.
# Usage: bash demo.sh   (run from the repo root)

BOLD='\033[1m'
DIM='\033[2m'
CYAN='\033[36m'
GREEN='\033[32m'
RED='\033[31m'
RESET='\033[0m'

# Make `ob` available without requiring the caller to pre-activate the venv.
if [ -f .venv/bin/activate ]; then
    # shellcheck disable=SC1091
    source .venv/bin/activate
elif ! command -v ob >/dev/null 2>&1; then
    echo -e "${RED}error:${RESET} .venv not found and 'ob' is not on PATH." >&2
    echo "Run setup first, from the repo root:" >&2
    echo "  uv venv && source .venv/bin/activate && uv pip install -e \".[dev]\"" >&2
    exit 1
fi

run() {
    echo ""
    echo -e "${CYAN}${BOLD}\$ $*${RESET}"
    echo -e "${DIM}─────────────────────────────────────────${RESET}"
    "$@" || echo -e "${DIM}(command exited with status $? — continuing demo)${RESET}"
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
