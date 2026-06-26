# Engineering Onboarding Copilot — Live Walkthrough Script

> 45-minute SA technical screen. Bookend slides frame the demo; live
> terminal + Cursor fill the middle. Everything runs locally — no
> network dependencies, no API keys, no external services.

## Pre-flight checklist

```bash
# Fresh terminal, clean state
cd ~/cursor-takehome-assignment
ob --version                         # CLI responds
pytest --tb=short -q                 # all green
ruff check .                         # clean
ls examples/bad-first-contrib/       # seeded violations present
ls examples/safe-first-contrib/      # clean example present
```

- [ ] Cursor open with repo loaded, rules active
- [ ] Terminal split visible alongside Cursor
- [ ] `docs/deck.md` rendered (Marp) or `docs/deck.pdf` open as backup
- [ ] Font size ≥ 16pt in terminal, readable at projector distance
- [ ] Rich output colors verified on projector (dark background)

---

## Opening Bookend — Slides (0:00–0:03)

**Surface:** Slide deck (Marp)

### Slide 1 — Title + Hook

Show project name. Narrate the pain:

> "New engineers lose days discovering conventions. Reviewers lose hours
> correcting avoidable issues. PM, QA, and DevOps lack visibility into
> how a change moves safely toward production. That's the tax this tool
> eliminates."

### Slide 2 — Architecture

Show the two-layer diagram. Narrate:

> "Two layers. Cursor workspace — rules and an MCP server — is what the
> engineer experiences in the IDE. The CLI is the deterministic engine
> that runs the same checks in CI. Both read from one source of truth:
> a YAML profile the team owns."

### Slide 3 — Approach (Built / Deferred / Why)

> "Here's what I built, what I deliberately didn't build, and why.
> I'll show you the artifact live, then we'll come back to tradeoffs
> at the end."

**Transition:** Close slides. Open Cursor full-screen with the repo loaded.

---

## Section 1 — The Hook: Catch a Bad Contribution (0:03–0:08)

**Surface:** Cursor (primary) + terminal (secondary)

**Goal:** The most memorable beat. Show a convention violation being caught
in real time — first by Cursor's rules, then by the CLI.

### In Cursor

1. Open `examples/bad-first-contrib/filters/_local_contrast.py` in the editor
2. Point out the violations visually (deprecated API, TODO-only body)
3. In Cursor chat/composer, ask: "Review this file against our scikit-image conventions"
4. The scikit-image-conventions rule activates → agent identifies the violations,
   quotes the convention, explains what to do instead

**Narration:**

> "This is a new engineer's first attempt. They used a deprecated API,
> left a TODO placeholder, imported from a private module, and skipped
> the test file. Watch what happens when they ask Cursor for help —
> the rules I configured catch all four issues and explain why."

### In Terminal

```bash
ob check examples/bad-first-contrib
```

5. Rich-formatted output shows the same 4 violations with rule IDs
6. Point at the output: "Same rules, no Cursor required. This is what
   CI sees."

**Fallback:** If Cursor rules don't activate cleanly, skip straight to the
terminal `ob check`. The CLI output is deterministic and will always work.
The rule moment can be re-attempted during the guardrails section.

**Key line:**

> "The business problem isn't 'generate code faster.' It's that this
> class of defect no longer reaches code review — and everyone else
> gets visibility without extra meetings."

---

## Section 2 — The Clean Path (0:08–0:13)

**Surface:** Terminal + Cursor file explorer

**Goal:** Show contrast — bad contribution vs. safe contribution. The
audience should feel the difference.

### Show the safe example

```bash
ob check examples/safe-first-contrib
```

1. Clean green pass. No violations. Point at the contrast.

### Show scaffold (if time)

```bash
ob scaffold --task "add adaptive histogram equalization helper"
```

2. New workspace appears under `workspaces/`
3. Open the generated PLAN.md in Cursor — show profile rule citations
4. Open the generated source stub and test stub

**Narration:**

> "One command would have prevented the previous disaster. The scaffold
> creates the right files in the right directories, with the right test
> structure, citing the conventions that apply. The new engineer starts
> from a correct baseline instead of guessing."

**Fallback:** If scaffold has any issues, skip it and just show the
pre-committed safe-first-contrib example. The contrast between bad and
good examples already tells the story.

---

## Section 3 — Multi-Audience Briefs (0:13–0:19)

**Surface:** Terminal (Rich output)

**Goal:** Show the same artifact producing four meaningfully different
views. This is the multi-audience differentiator.

```bash
ob brief --role engineer --workspace examples/safe-first-contrib
ob brief --role pm --workspace examples/safe-first-contrib
ob brief --role qa --workspace examples/safe-first-contrib
ob brief --role devops --workspace examples/safe-first-contrib
```

1. Run each in quick succession (or use a wrapper that runs all four)
2. Do NOT read every line. Point at the key differences:
   - Engineer: file map + implementation checklist
   - PM: user/business impact + scope + "what to ask in kickoff"
   - QA: edge cases + test strategy + "test names we will reject"
   - DevOps: CI guardrails + pipeline signal + boundary enforcement

**Narration:**

> "Same artifact. Four different views. The PM doesn't see implementation
> details. QA doesn't see business justification. Each role gets exactly
> what they need to make their decision. Zero extra meetings."

**Key line:**

> "This is what the prompt means by 'multiple audiences.' Not four
> copies of the same document — four genuinely different perspectives
> on the same change."

---

## Section 4 — Live Mutation: Profile Edit (0:19–0:25)

**Surface:** Cursor (editing) + terminal (verification)

**Goal:** Prove maintainability. The team owns the profile. Changing a
convention immediately changes what the tool enforces. No code changes.

### In Cursor

1. Open `profiles/scikit-image.yaml`
2. Live edit: add a new deprecated API entry (e.g., mark `skimage.filters.median`
   as deprecated with replacement `skimage.filters.rank.median`)
3. Save the file

### In Terminal

```bash
ob check examples/bad-first-contrib
```

4. Re-run check — the new deprecation warning appears in the output
5. Point at it: "I changed one line in the YAML. Every engineer, every
   pipeline, and every Cursor rule now enforces this new convention."

**Narration:**

> "The platform team owns one file. Change it here, and every new
> engineer and every pipeline sees it. No PRs to my code. No
> redeployment. The team that knows the conventions owns the rules."

**Fallback:** The profile edit is deterministic and will always work.
This section has very low demo risk.

---

## Section 5 — Guardrails: Approved Boundaries (0:25–0:28)

**Surface:** Terminal

**Goal:** Demonstrate that the tool enforces real boundaries, not just
suggestions. Show a refusal.

```bash
# Attempt to scaffold outside approved directories
ob scaffold --task "add helper to skimage/_vendored/"
```

1. Tool refuses with a clear explanation: directory not in approved list
2. Show the approved directories in the profile YAML

**Narration:**

> "The prompt asks about 'approved context boundaries.' This isn't a
> suggestion — it's enforcement. The tool won't create files outside
> the directories the profile allows. Same philosophy as the MCP server:
> restrict what the agent can see, not just what it produces."

---

## Section 6 — CI: Same Checks, Production Path (0:28–0:31)

**Surface:** Browser (GitHub Actions) or terminal

**Goal:** Close the SDLC loop. The same `ob check` runs in CI.

1. Show `.github/workflows/ci.yml` briefly in Cursor (don't read it line by line)
2. Show a green CI run on GitHub (pre-pushed)
3. Point at the step summary: role briefs visible in the Actions tab

**Narration:**

> "The exact same `ob check` command the engineer runs locally is the one
> that blocks the PR. Ruff and pytest are there too. The role briefs
> appear in the GitHub Actions summary — the PM sees the PM brief without
> cloning the repo."

**Fallback:** If GitHub isn't accessible, show the CI YAML and run the
same commands locally: `ob check && pytest && ruff check .`

---

## Closing Bookend — Slides (0:31–0:38)

**Surface:** Slide deck (Marp)

### Slide 4 — Tradeoffs + Limitations

> "Let me be honest about where this breaks."

Narrate each limitation briefly:
- Deterministic by design — no LLM in the CLI. "I made this choice
  deliberately. Pushing LLM calls out of sight isn't the right call
  when agentic development is already the focal point. Better to have
  transparency about what's happening token-wise."
- Single-profile scope — one library at a time
- Template-driven briefs — they don't read the candidate code yet
- Hand-curated conventions — no automated convention discovery
- No multi-file refactor support

For each: "Here's how I'd address it in a real engagement."

### Slide 5 — Extensibility + Round 4

> "The assignment says this artifact is the foundation for the final
> challenge — extending it to a customer scenario."

Show the diffusers stub profile reference. Narrate:

> "Swap the YAML, keep the engine. A new customer library means a new
> profile, not a new tool. The Cursor rules reference the profile, the
> CLI reads the profile, the MCP server exposes the profile. One file
> change, three surfaces updated."

### Slide 6 — Close

Land the quotable line:

> "Most candidates build a coding assistant for one engineer. I built
> a convention-aware SDLC workflow that turns the team's tribal knowledge
> into an executable artifact — owned by the team, usable by PM, QA,
> and DevOps, and extensible to any library by swapping a YAML profile."

Pause. Then:

> "Questions?"

---

## Buffer + Q&A (0:38–0:45)

**Prepared answers for likely questions:**

### "Why scikit-image over OpenCV?"

> "scikit-image is Python-native with deliberately uniform conventions —
> numpydoc everywhere, snake_case everything, mandatory gallery examples,
> two-approval mentorship reviews. That uniformity is what makes it an
> ideal target for a copilot that learns project norms. OpenCV's value
> would be showing complexity handling, but the C++/Python binding
> boundary makes it harder to demo a clean contribution path."

### "Why no LLM in the CLI?"

> "Deliberate choice. The CLI is the deterministic, reproducible layer
> the team owns. LLMs already power the Cursor agent through the rules
> I configured. Pushing more LLM calls into the CLI would add opacity
> without adding value — the engineer can't inspect or override what
> the model decided. The profile YAML is inspectable. The check rules
> are inspectable. That's the point."

### "How do you keep the profile current?"

> "Same way you keep any configuration current — it's checked in, it
> goes through code review, and the team that knows the conventions
> owns it. In a real engagement, I'd connect convention discovery to
> the library's changelog or deprecation warnings, but the manual
> curation is the right starting point."

### "What would you do for a real internal library?"

> "Same architecture. Index their approved docs for the MCP server.
> Write their profile YAML from their contribution guide and style
> guide. Configure the Cursor rules. The engine doesn't change."

### "How does this use Cursor specifically?"

> "Three ways. The rules I wrote make the agent convention-aware in
> the editor — that's the catch-the-violation moment you saw. The MCP
> server feeds approved conventions into Cursor's context engine so the
> agent can reference them. And the CLI is callable as a tool from
> Cursor's agent for deterministic operations. The artifact isn't just
> built with Cursor — it's built for Cursor."

### "Where does it break?"

> (Open docs/known-limitations.md and read from it. Don't improvise.)

---

## Timing Budget

| Section | Minutes | Cumulative | Risk Level |
|---------|---------|------------|------------|
| Opening slides | 3 | 0:03 | Low |
| Hook: bad contribution | 5 | 0:08 | Medium (Cursor rule) |
| Clean path + scaffold | 5 | 0:13 | Low |
| Multi-audience briefs | 6 | 0:19 | Low |
| Live mutation | 6 | 0:25 | Low |
| Guardrails | 3 | 0:28 | Low |
| CI | 3 | 0:31 | Low |
| Closing slides | 7 | 0:38 | Low |
| Buffer + Q&A | 7 | 0:45 | — |

**Total demo risk:** One medium-risk moment (Cursor rule activation in
Section 1). Everything else is deterministic. Fallback: skip to terminal
`ob check` if the rule doesn't fire.

---

## Demo Anti-Patterns to Avoid

1. **Don't read code line by line.** Point at structure, not syntax.
2. **Don't explain what you're about to type.** Type it, then explain
   what happened.
3. **Don't apologize for limitations.** State them matter-of-factly.
   Limitations you chose are judgment signals, not weaknesses.
4. **Don't show all four briefs in full.** Show one fully, then flash
   the other three to prove differentiation. The audience gets it.
5. **Don't live-code anything.** Every command is pre-tested. The only
   live edit is the profile YAML change, which is one line.
6. **Don't alt-tab to a browser unnecessarily.** Cursor + terminal
   should cover 90% of the demo. Browser only for GitHub CI if needed.
