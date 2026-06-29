# Engineering Onboarding Copilot

A convention-aware SDLC workflow that turns a team's tribal knowledge into an
executable artifact — owned by the team, usable by PM/QA/DevOps, and extensible
to any library by swapping a YAML profile.

## What It Does

Two layers, one source of truth:

```
┌─────────────────────────────────────┐
│  Cursor Workspace (IDE layer)       │
│  • Cursor rules per SDLC stage      │
│  • FastMCP server for conventions   │
│  ↕ reads from ↕                     │
│  profiles/scikit-image.yaml         │
│  ↕ reads from ↕                     │
│  CLI Engine (ob)                    │
│  • ob scaffold · ob check · ob brief│
└─────────────────────────────────────┘
          ↓ same checks ↓
     GitHub Actions CI Pipeline
```

**Profile-driven.** The team owns the YAML. The engine owns the logic.

**100% deterministic.** No LLM calls in the CLI. Cursor's agent handles
the agentic interaction through the rules configured in this workspace.

## Quick Start

```bash
git clone git@github.com:kevglynn/cursor-takehome-assignment.git
cd cursor-takehome-assignment

# macOS / Linux
uv venv && source .venv/bin/activate
# Windows (PowerShell): uv venv; .venv\Scripts\Activate.ps1

uv pip install -e ".[dev]"

ob --version          # verify installation
pytest -v             # run all tests
ruff check .          # verify lint
```

Open the repo in **Cursor** for the full onboarding experience — the rules
and MCP server activate automatically.

## CLI Commands

```bash
# Check a workspace against conventions
ob check examples/bad-first-contrib     # 5 violations found
ob check examples/safe-first-contrib    # all checks passed

# Create a new contribution workspace
ob scaffold --task "add adaptive histogram equalization helper"

# Generate role-specific briefs
ob brief --role engineer --workspace examples/safe-first-contrib
ob brief --role pm --workspace examples/safe-first-contrib
ob brief --role qa --workspace examples/safe-first-contrib
ob brief --role devops --workspace examples/safe-first-contrib
```

## Architecture

### Profile (`profiles/scikit-image.yaml`)
Team-owned YAML defining approved directories, forbidden paths, deprecated
APIs, testing conventions, docstring style, and role brief templates.

### CLI (`ob`)
Three commands — `scaffold`, `check`, `brief`. All read from the profile.
All deterministic. Runs the same in the terminal and in CI.

### Cursor Rules (`.cursor/rules/`)
SDLC-stage rules that activate based on file patterns:
- `scikit-image-conventions.mdc` — enforces conventions on `*.py`
- `sdlc-planning.mdc` — planning guidance on `PLAN.md`
- `sdlc-implementation.mdc` — implementation on `skimage/**/*.py`
- `sdlc-testing.mdc` — testing on `test_*.py`
- `sdlc-review.mdc` — review on `BRIEFS.md`

### MCP Server (`src/ob/mcp_server.py`)
FastMCP server exposing 7 convention resources to Cursor's context engine.
Cursor's agent can reference approved directories, deprecated APIs,
docstring templates, and more — all sourced from the profile YAML.

**How Cursor loads it:** `.cursor/mcp.json` registers the server as a stdio
MCP server, launched with the project's virtualenv interpreter:

```json
{
  "mcpServers": {
    "onboarding-copilot": {
      "type": "stdio",
      "command": "${workspaceFolder}/.venv/bin/python",
      "args": ["-m", "ob.mcp_server"]
    }
  }
}
```

Run the documented setup first (so `.venv` exists), then reload Cursor. The
server appears under Settings → MCP. Verify the 7 resources are served:

```bash
# Exercises the wired server end-to-end (lists resources over MCP):
pytest tests/test_mcp_server.py::TestMCPServerRegistration -q
```

### CI (`.github/workflows/ci.yml`)
Runs ruff, pytest, `ob check` on both examples, and generates role briefs
to `$GITHUB_STEP_SUMMARY`.

## File Structure

```
├── src/ob/                    # CLI + MCP server source
│   ├── cli.py                 # Typer CLI entry point
│   ├── commands/              # scaffold, check, brief
│   ├── models.py              # Pydantic profile models
│   ├── profile.py             # YAML loader
│   ├── guardrails.py          # Path boundary enforcement
│   └── mcp_server.py          # FastMCP server
├── profiles/
│   ├── scikit-image.yaml      # Primary profile
│   └── diffusers.yaml         # Stub proving extensibility
├── examples/
│   ├── bad-first-contrib/     # Seeded violations (demo)
│   └── safe-first-contrib/    # Clean example (demo)
├── tests/                     # 107 tests
├── docs/
│   ├── demo.md                # 45-min walkthrough script
│   ├── deck.md                # Marp slide deck (6 slides)
│   ├── deck.pdf               # Pre-rendered PDF backup
│   ├── decisions.md           # ADR-style decision log
│   ├── deployment-guide.md    # Rollout path for real orgs
│   └── known-limitations.md   # 8 honest limitations
├── .cursor/
│   ├── rules/                 # SDLC-stage Cursor rules
│   └── mcp.json               # Registers the MCP server with Cursor
├── .github/workflows/ci.yml   # CI pipeline
├── demo.sh                    # Demo launcher (macOS/Linux)
├── demo.ps1                   # Demo launcher (Windows/PowerShell)
├── LICENSE                    # MIT
└── pyproject.toml             # Project config
```

## Limitations

See [docs/known-limitations.md](docs/known-limitations.md) for the full list.
Key tradeoffs:

1. Deterministic checks only — no semantic code understanding
2. Single-profile scope — one library at a time
3. Template-driven briefs — metadata, not code-aware
4. Hand-curated conventions — no automated discovery
5. No multi-file refactor support

Each is a deliberate choice with a documented remediation path.

## Decisions

See [docs/decisions.md](docs/decisions.md) for the ADR-style log behind every
architectural choice (deterministic CLI, MCP-as-core, `ob` naming,
profile-driven design, scikit-image over OpenCV, demo-script-as-spec, and
CI-delivered briefs) — each with context, rationale, and alternatives.

## Deployment

See [docs/deployment-guide.md](docs/deployment-guide.md) for how to roll this
out at a real organization — roles, minimum viable profile, CI integration,
success metrics, and rollout sequence.

## Demo

See [docs/demo.md](docs/demo.md) for the full 45-minute walkthrough script.
Quick version:

```bash
bash demo.sh        # macOS / Linux
pwsh -File demo.ps1 # Windows (PowerShell)
```

## License

[MIT](LICENSE).
