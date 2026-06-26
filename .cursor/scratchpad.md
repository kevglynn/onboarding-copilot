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

### Phase 2 — Interview-hardening (EXECUTED): Epic `cursor-takehome-assignment-8ut`

Goal: zero gap between what the demo NARRATES and what is actually true.

| Bead | Title | Deps | Priority | Status |
|------|-------|------|----------|--------|
| 8ut.1 | CI runs green on GitHub (Actions enabled + MCP deps) | none | P0 | ✓ closed — CLI-confirmed green (run 28242226261) |
| 8ut.2 | Wire MCP server into Cursor via .cursor/mcp.json | none | P1 | ✓ closed |
| 8ut.3 | Verify + harden live Cursor-rule "catch" moment (centerpiece) | none | P0 | ◐ artifacts DONE — awaiting USER live rehearsal |
| 8ut.4 | Fix scaffold target-directory inference (substring bug) | none | P2 | ✓ closed |
| 8ut.5 | Elevation: expose `ob check` as an MCP tool | 8ut.2 | P2 | ✓ closed |
| 8ut.7 | Consolidated decision log (docs/decisions.md) | none | P2 | ✓ closed |
| 8ut.6 | Capstone: cold-start clone + demo-to-reality audit | 8ut.1-.5, 8ut.7 | P1 | ◐ audit run + PASS — blocked by 8ut.1/.3 (by design) |
| 8ut.8 | Profile-driven rule-ID namespace (rule_prefix) | discovered-from 8ut.6 | P2 | ✓ closed |
| 8ut.9 | "Just works" agent discoverability | none | P1 | ✓ closed |

All beads pass `bd lint`. No dependency cycles.

Refinements applied: (a) fastmcp moved [mcp]→[dev] so one install group covers
dev/CI/fresh-clone; (b) CI pins `uv venv --python 3.12`; (c) 8ut.6 demonstrates
the profile swap via `ob check --profile profiles/diffusers.yaml`.

NEW during audit (8ut.8): the rule-ID namespace was hardcoded "SK-*" even under
the diffusers profile, which silently undercut the "nothing is hardcoded to
scikit-image" centerpiece. Fixed: `rule_prefix` is now profile-owned. Same
workspace now yields 5 `SK-*` (scikit-image) vs 2 `DIFF-*` (diffusers).

NEW (8ut.9): Every onboarding copilot rule was alwaysApply:false — an agent
entering the workspace learned how to manage beads but had zero awareness of the
copilot, MCP, or CLI. Fixed: alwaysApply:true spine rule (`onboarding-copilot.mdc`)
connects agents to MCP tool+resources, CLI, profile YAML, and SDLC rules on first
contact. SDLC globs widened (implementation was targeting a nonexistent skimage/ path).
AGENTS.md now has a copilot section for non-Cursor agents. CI bumped checkout@v5.

## Honest Audit Findings (post-build) — resolution status

1. **CI is absent AND would fail.** GitHub Actions endpoints return 404 (not
   running); the `test` job installs `.[dev]` but fastmcp is in `.[mcp]`, so
   MCP tests would ImportError. Contradicts demo.md line 242. → 8ut.1
   *RESOLVED + closed. Fixed in code (fastmcp→[dev], py3.12 pin) AND
   CLI-confirmed green: run 28242226261 on main, all 5 jobs success, Test job
   ran test_mcp_server.py → 77 passed in 3.11s. The earlier 404 was a STALE
   SESSION, not a permanent token limit — `gh auth status` now shows
   repo+workflow scopes. No browser-only IOU.*
2. **MCP not connected to Cursor.** No `.cursor/mcp.json`; the server is
   code-only. Contradicts demo.md lines 343-345. → 8ut.2 *RESOLVED + closed.*
3. **Centerpiece unverified.** The live Cursor-rule catch (demo Section 1,
   the "strong yes" moment) has never been confirmed in the Cursor runtime.
   → 8ut.3 *Artifacts + rehearsal protocol + deterministic fallback DONE.
   AWAITING USER live rehearsal inside Cursor.*
4. **Scaffold inference bug.** "histogram equalization" routes to `skimage/io/`
   because "io" is a substring of "equalizatION". → 8ut.4 *RESOLVED + closed
   (word-boundary + keyword-map routing; regression test added).*
5. **(found during 8ut.6 audit) Rule-ID prefix hardcoded.** Swapping to the
   diffusers profile still printed `SK-*` IDs, undercutting the centerpiece
   swap claim. → 8ut.8 *RESOLVED + closed (`rule_prefix` is profile-owned;
   5 `SK-*` vs 2 `DIFF-*` on the same workspace).*

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
- [x] Phase 2 hardening epic + beads created, linted, dependency-graphed
- [x] Phase 2 EXECUTED: 8ut.1, .2, .4, .5, .7, .8, .9 closed with evidence
- [x] 8ut.1 CI green — CLI-confirmed (run 28242226261, all 5 jobs success,
      MCP tests ran → 77 passed in CI). gh token was fine; 404 was stale session.
- [x] 8ut.6 capstone audit RUN and PASSED (fresh clone; 77 tests; all demo
      commands reproducible; profile swap 5 `SK-*` vs 2 `DIFF-*`)
- [x] 8ut.9 "Just works" — always-on spine rule, SDLC globs widened, AGENTS.md
      copilot section, stale refs fixed, CI checkout@v5
- [x] Code/test/lint state: 77 tests pass, ruff clean (verified in real venv)
- [x] Committed + pushed to origin/main (cb5f0df + 9eacae6); deck.pdf re-rendered
- [ ] 8ut.3 — USER: live-rehearse the Cursor-rule catch (protocol in
      docs/cursor-rule-verification.md); deterministic CLI fallback exists
- [ ] 8ut.6 — unblocks + closes once 8ut.3 closes (capstone already run/passed)
- [ ] Uncommitted: 8ut.9 changes (just-works rules, AGENTS.md, CI bump, stale refs)

## Executor's Feedback or Assistance Requests

Phase 2 executed. 8ut.9 ("just works") addressed the biggest UX gap: agents
entering the workspace now discover the copilot, MCP, and CLI automatically via
an alwaysApply:true spine rule + AGENTS.md copilot section. CI bumped to
checkout@v5 (Node24, no deprecation). ONE item remains for the USER:

1. **8ut.3** — perform the live in-Cursor rehearsal of the centerpiece catch
   (protocol: docs/cursor-rule-verification.md; deterministic CLI fallback ready).

Once 8ut.3 is confirmed, 8ut.6 unblocks and closes (capstone already run +
passed), then the epic `8ut` closes.

## Lessons

- `gh repo create --source=.` sets a malformed remote when repo already exists — fix with `git remote set-url`
- Council cross-pollination is high-value: all 5 voices independently flagged "where is Cursor?" as the critical gap
- The Hiring Manager's "strong yes" test is specific and actionable: a live Cursor rule catching a real convention violation
- Simplifier vs Skeptic on MCP: genuine tension resolved by user decision (core deliverable)
- Don't declare a tooling blocker (e.g. "gh token can't read the repo") from a
  single failed call — verify with `gh auth status` / `gh auth token` in the
  ACTUAL shell first. The 404 here was a stale session, not a permission limit;
  the token had repo+workflow all along. Re-check before writing an IOU.
