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

Epic: `cursor-takehome-assignment-pbq` — Engineering Onboarding Copilot

| Bead | Title | Deps | Priority |
|------|-------|------|----------|
| pbq.1 | Demo walkthrough script + pre-baked examples | none | P0 |
| pbq.2 | Foundation: project scaffold + scikit-image profile | pbq.1 | P1 |
| pbq.3 | CLI engine: scaffold + check + brief commands | pbq.2 | P1 |
| pbq.4 | Cursor workspace: rules per SDLC stage + MCP server | pbq.2 | P1 |
| pbq.5 | CI pipeline + role-brief delivery | pbq.3 | P2 |
| pbq.6 | Demo rehearsal + polish | pbq.3, pbq.4, pbq.5 | P2 |

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

- [x] Planning conversation captured
- [x] GitHub repo created (private, kevglynn/cursor-takehome-assignment)
- [x] Playbook scaffolding complete
- [x] Council analysis complete (2 rounds, 5 voices)
- [x] Beads backlog created with rich ACs
- [x] Battle cards created (docs/library-battle-cards.md)
- [ ] Implementation not started
- [ ] Next: claim pbq.1 (demo walkthrough script)

## Executor's Feedback or Assistance Requests

Ready to begin execution. `bd ready` shows pbq.1 is the next claimable bead.

## Lessons

- `gh repo create --source=.` sets a malformed remote when repo already exists — fix with `git remote set-url`
- Council cross-pollination is high-value: all 5 voices independently flagged "where is Cursor?" as the critical gap
- The Hiring Manager's "strong yes" test is specific and actionable: a live Cursor rule catching a real convention violation
- Simplifier vs Skeptic on MCP: genuine tension resolved by user decision (core deliverable)
