# Decision Log

ADR-style record of the architectural decisions behind the Engineering
Onboarding Copilot. Each entry: **Context → Decision → Rationale →
Alternatives considered → Status**. This is the one-screen reference for
defending every choice during the live walkthrough and Q&A.

---

## ADR-001 — The CLI is 100% deterministic (no LLM inside `ob`)

**Context.** Agentic development is the focal point of the assignment. It is
tempting to put LLM calls inside the CLI (e.g. "ask a model whether this code
follows conventions").

**Decision.** `ob` contains zero LLM calls. Every check is rule-based: AST
analysis for imports, deprecated-API usage, and TODO-only bodies; docstring
section/style checks; and file-existence tests. All LLM interaction happens
through Cursor's own agent, driven by the rules and MCP server.

**Rationale.** The CLI is the reproducible, inspectable layer the team owns —
the same result in the terminal and in CI, every time. Hiding more model calls
inside the tool would add opacity and token cost without adding value, exactly
where the engineer most needs to trust and audit the output. The profile YAML
and the check rules are both inspectable; that auditability is the point.

**Alternatives considered.** (a) LLM-powered semantic review in the CLI —
rejected as non-deterministic and opaque; it belongs in the Cursor agent
layer. (b) Hybrid (LLM with deterministic fallback) — rejected as added
complexity for a demo whose strength is a clear separation of concerns.

**Status.** Accepted. Semantic review is a documented extension point
(see [`known-limitations.md`](known-limitations.md) §1).

---

## ADR-002 — The MCP server is a core deliverable, not an add-on

**Context.** The artifact must be "built for Cursor," not merely built with
Cursor. Cursor consumes context through rules and through MCP servers.

**Decision.** Ship a FastMCP server that exposes the profile as 7 read-only
convention resources **and** a `check_workspace` tool, wired into Cursor via
`.cursor/mcp.json`.

**Rationale.** The MCP server is the most direct demonstration of understanding
Cursor's context architecture: the same profile that drives the CLI and the
rules is served into the agent's context. The tool endpoint lets the agent run
the deterministic checker itself, closing the loop between "read conventions"
and "enforce conventions."

**Alternatives considered.** (a) Rules-only (skip MCP) — rejected; it would
miss the strongest Cursor-native signal. (b) MCP resources only (no tool) —
shipped first, then elevated; exposing `check` as a tool turned a stated
limitation into a differentiator.

**Status.** Accepted. `scaffold`/`brief` as MCP tools remain an extension
point (see [`known-limitations.md`](known-limitations.md) §7).

---

## ADR-003 — Name the CLI `ob` (short for "onboard")

**Context.** The tool is invoked constantly in the live demo, so the name is
typed and spoken repeatedly.

**Decision.** Name the CLI `ob`.

**Rationale.** No collision with common Unix commands, short enough to type
fluidly during a live demo, and it reads as "onboard" — the product's purpose.
Avoids name ambiguity with existing tooling.

**Alternatives considered.** (a) `onboard` — clearer but longer to type live.
(b) `copilot`/`assistant` — overloaded terms with collision and trademark
ambiguity. (c) `skimage-cli` — ties the name to one library, contradicting the
profile-driven extensibility story (ADR-004).

**Status.** Accepted.

---

## ADR-004 — Profile-driven architecture (one YAML, three surfaces)

**Context.** The artifact is explicitly the foundation for a later
customer-scenario extension. It must adapt to a new library without a rewrite.

**Decision.** A single YAML profile (`profiles/<library>.yaml`) is the source
of truth for conventions. The CLI reads it, the Cursor rules reference it, and
the MCP server exposes it. Adding a library means adding a profile, not a tool.

**Rationale.** This is the architectural ace: "swap the YAML, keep the engine."
It keeps conventions team-owned (checked in, code-reviewed) and demonstrates
extensibility concretely — a `diffusers.yaml` stub proves a second library
drops in. One file change updates three surfaces. The proof is observable:
the same `bad-first-contrib` workspace yields 5 `SK-*` violations under
scikit-image and 2 `DIFF-*` violations under diffusers — even the rule-ID
namespace (`rule_prefix`) is profile-owned, so nothing is hardcoded to one
library.

**Alternatives considered.** (a) Hard-coded conventions in Python — rejected;
not team-ownable, not extensible. (b) A database/service of conventions —
rejected as over-engineering for the scope; a checked-in file is inspectable
and version-controlled.

**Status.** Accepted. Multi-profile composition (monorepos) is an extension
point (see [`known-limitations.md`](known-limitations.md) §2).

---

## ADR-005 — Target scikit-image (over OpenCV)

**Context.** The copilot needs a real open-source library with conventions
worth enforcing.

**Decision.** Build the primary profile for scikit-image.

**Rationale.** scikit-image is Python-native with deliberately uniform,
well-documented conventions — numpydoc everywhere, `snake_case` throughout,
mandatory gallery examples, and a structured contribution/review process.
That uniformity is exactly what a convention-aware copilot can encode and
enforce cleanly, which makes for a crisp demo of a safe first contribution.

**Alternatives considered.** OpenCV — its value would be showing complexity
handling, but the C++/Python binding boundary and less uniform conventions
make a clean, demonstrable contribution path harder. scikit-image's numpydoc
docstrings, `snake_case` API, per-module `tests/` layout, and explicit
deprecation policy each map directly onto a profile rule; OpenCV's mixed
C++/Python surface and looser Python conventions would dilute that one-to-one
mapping and weaken the demo.

**Status.** Accepted.

---

## ADR-006 — Demo script is the spec (build backward from the walkthrough)

**Context.** The deliverable is judged in a live 45-minute walkthrough, not as
a library someone reads.

**Decision.** Author the demo walkthrough first (`docs/demo.md`) and build the
artifact backward from it. Every command in the script must produce the output
the script describes.

**Rationale.** Designing the walkthrough first keeps scope honest — only what
the demo needs gets built — and makes "the demo script is the spec" a literal
verification target. The cold-start + demo-to-reality audit checks every
scripted command against actual behavior.

**Alternatives considered.** Build features first, script later — rejected; it
invites scope creep and risks a polished tool with a weak narrative.

**Status.** Accepted.

---

## ADR-007 — Deliver role briefs through the CI step summary

**Context.** The artifact must serve four audiences — engineer, PM, QA,
DevOps — and that multi-audience claim needs to be observable, not asserted.

**Decision.** The CI pipeline generates the PM, QA, and DevOps briefs and
writes them to `$GITHUB_STEP_SUMMARY`, so they render in the GitHub Actions
run.

**Rationale.** It makes the "different views for different roles" claim
concrete in the production path: a PM sees the PM brief in the same place the
DevOps engineer sees the pipeline signal. The brief content is template-driven
and deterministic, consistent with ADR-001.

**Alternatives considered.** (a) Briefs only in the terminal — rejected; less
visible to non-engineer audiences. (b) A separate web UI — rejected as scope
creep; the step summary is where these audiences already look.

**Status.** Accepted. Code-aware brief content is an extension point
(see [`known-limitations.md`](known-limitations.md) §3).
