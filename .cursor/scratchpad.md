# Agent Scratchpad

## Background and Motivation

Cursor Solutions Architect take-home assignment (3rd round, technical).
Build: **Engineering Onboarding Copilot** — a two-layer system (Cursor workspace + deterministic CLI `ob`) that guides new engineers through safe first contributions to scikit-image.

The artifact must demonstrate the full SDLC path and serve four audiences (engineer, PM, QA, DevOps). Presented in a 45-minute live walkthrough.

## Key Challenges and Analysis

Council of 5 voices (Advocate/Opus, Skeptic/Gemini, Simplifier/GPT, Hiring Manager/Sonnet, Demo Coach/Grok) conducted two rounds of adversarial analysis. Key convergences:

1. **Cursor is the protagonist; CLI is the engine.** The repo opened in Cursor should BE the onboarding experience.
2. **100% deterministic CLI.** LLM interaction only through Cursor's own agent. Deliberate design choice — transparency about what's happening LLM-/token-wise.
3. **Profile-driven architecture.** Conventions in YAML, team-owned, extensible by swapping profiles. The architectural ace for round 4.
4. **FastMCP server** exposes conventions as resources to Cursor's context engine (core deliverable).
5. **Demo script is the spec.** Design the walkthrough first, build backward from it.
6. **The "strong yes" moment:** a live Cursor rule catches a convention violation in the editor, explained in customer deployment language.

## High-level Task Breakdown

### Phase 1 — Build (COMPLETE): Epic `cursor-takehome-assignment-pbq`

| Bead | Title | Deps | Priority | Status |
|------|-------|------|----------|--------|
| pbq.1 | Demo walkthrough script + pre-baked examples | none | P0 | ✓ closed |
| pbq.2 | Foundation: project scaffold + scikit-image profile | pbq.1 | P1 | ✓ closed |
| pbq.3 | CLI engine: scaffold + check + brief commands | pbq.2 | P1 | ✓ closed |
| pbq.4 | Cursor workspace: rules per SDLC stage + MCP server | pbq.2 | P1 | ✓ closed |
| pbq.5 | CI pipeline + role-brief delivery | pbq.3 | P2 | ✓ closed |
| pbq.6 | Demo rehearsal + polish | pbq.3, pbq.4, pbq.5 | P2 | ✓ closed |
| pbq.7 | Bookend slide deck (Marp markdown + PDF backup) | pbq.1 | P1 | ✓ closed |

Result: complete skeleton, 61 local tests passing, ruff clean. BUT an honest
audit found the artifact is NOT yet a "knockout" — three claims are not wired
up and one correctness bug exists. See Honest Audit Findings below.

### Phase 2 — Interview-hardening (PLANNED): Epic `cursor-takehome-assignment-8ut`

Goal: zero gap between what the demo NARRATES and what is actually true.

| Bead | Title | Deps | Priority |
|------|-------|------|----------|
| 8ut.1 | CI runs green on GitHub (Actions enabled + MCP deps) | none | P0 |
| 8ut.2 | Wire MCP server into Cursor via .cursor/mcp.json | none | P1 |
| 8ut.3 | Verify + harden live Cursor-rule "catch" moment (centerpiece) | none | P0 |
| 8ut.4 | Fix scaffold target-directory inference (substring bug) | none | P2 |
| 8ut.5 | Elevation: expose `ob check` as an MCP tool | 8ut.2 | P2 |
| 8ut.7 | Consolidated decision log (docs/decisions.md) | none | P2 |
| 8ut.6 | Capstone: cold-start clone + demo-to-reality audit | 8ut.1-.5, 8ut.7 | P1 |

All 8 beads (epic + 7) pass `bd lint`. No dependency cycles.

Locked refinements: (a) move fastmcp [mcp]→[dev] so one install group covers
dev/CI/fresh-clone; (b) enabling GitHub Actions may need a one-time repo-settings
toggle by the owner; (c) 8ut.6 demonstrates the profile swap via
`ob check --profile diffusers.yaml`.

Execution order: 8ut.1 + 8ut.3 (P0) → 8ut.2 → 8ut.5 → 8ut.4 → 8ut.7 → 8ut.6.

## Honest Audit Findings (post-build)

1. **CI is absent AND would fail.** GitHub Actions endpoints return 404 (not
   running); the `test` job installs `.[dev]` but fastmcp is in `.[mcp]`, so
   MCP tests would ImportError. Contradicts demo.md line 242. → 8ut.1
2. **MCP not connected to Cursor.** No `.cursor/mcp.json`; the server is
   code-only. Contradicts demo.md lines 343-345. → 8ut.2
3. **Centerpiece unverified.** The live Cursor-rule catch (demo Section 1,
   the "strong yes" moment) has never been confirmed in the Cursor runtime.
   → 8ut.3
4. **Scaffold inference bug.** "histogram equalization" routes to `skimage/io/`
   because "io" is a substring of "equalizatION". → 8ut.4

## Alignment Decisions (locked)

| Decision | Resolution | Rationale |
|----------|-----------|-----------|
| MCP | Core deliverable | Proves understanding of Cursor's context architecture |
| CLI name | `ob` (short for onboard) | No Unix collision, short, clear |
| LLM | 100% deterministic CLI | Transparency; agentic dev is already the focal point |
| Second profile | Stub for HuggingFace diffusers | Proves extensibility, not fully fleshed |
| Brief delivery | $GITHUB_STEP_SUMMARY | Multi-audience claim becomes observable |
| Build order | Demo script first as spec | Council-unanimous: design the walkthrough, build backward |

## Current Status / Progress Tracking

- [x] Phase 1 build complete (pbq.1–pbq.7 all closed, pushed to main)
- [x] Honest audit performed; gaps identified
- [x] Phase 2 hardening epic + 6 beads created, linted, dependency-graphed
- [ ] Phase 2 execution NOT started — awaiting go / mode confirmation
- [ ] Next claimable: 8ut.1 (CI), 8ut.3 (centerpiece) — both P0

## Executor's Feedback or Assistance Requests

Phase 2 planned and scoped. Suggested execution order (respecting deps and
priority): 8ut.1 (CI honesty) and 8ut.3 (centerpiece) first as P0, then 8ut.2
(MCP wiring) → 8ut.5 (MCP tool), 8ut.4 (scaffold), then 8ut.6 (capstone audit)
last. 8ut.3 has a manual in-Cursor confirmation step only the user can perform.
Awaiting confirmation to proceed in Executor mode.

## Lessons

- `gh repo create --source=.` sets a malformed remote when repo already exists — fix with `git remote set-url`
- Council cross-pollination is high-value: all 5 voices independently flagged "where is Cursor?" as the critical gap
- The Hiring Manager's "strong yes" test is specific and actionable: a live Cursor rule catching a real convention violation
- Simplifier vs Skeptic on MCP: genuine tension resolved by user decision (core deliverable)
