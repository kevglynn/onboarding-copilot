# Verifying the Live Cursor-Rule "Catch" (Demo Centerpiece)

This is the highest-impact, highest-risk beat of the demo (docs/demo.md
Section 1): a Cursor rule catching a convention violation live in the editor.
LLM responses are non-deterministic, so this must be **rehearsed**, and it has
a **deterministic fallback** that always works.

## What makes the catch fire

- Rule file: `.cursor/rules/scikit-image-conventions.mdc`
- Trigger: `globs: "**/*.py"`, `alwaysApply: false` → the rule auto-attaches
  whenever a `.py` file matching the glob is in the agent's context.
- The rule's "When asked to review a file" section instructs the agent to
  report violations using the same `SK-*` IDs that `ob check` emits.

## Pre-demo verification protocol (run this before the interview)

1. **Open the seeded bad file in Cursor:**
   `examples/bad-first-contrib/filters/_local_contrast.py`

2. **Confirm the rule is attached.** In the Cursor chat/agent panel, verify
   `scikit-image-conventions` appears as an active/attached rule for this file.
   (You can also `@scikit-image-conventions` explicitly to force-attach.)

3. **Type this exact prompt to the agent:**

   > Review this file against our scikit-image conventions and list every
   > violation with its rule ID.

4. **Expected agent behavior** — it should enumerate these five violations,
   each with the matching `SK-*` ID:

   | Rule ID | Violation in the file |
   |---------|----------------------|
   | SK-D-001 | `from skimage.filters import median` — deprecated; use `skimage.filters.rank.median` |
   | SK-F-001 | `from skimage._shared.utils import ...` — import from forbidden `_shared` |
   | SK-I-001 | `local_contrast_normalize` body is a `# TODO` + `pass` (no real logic) |
   | SK-T-002 | No `tests/test_local_contrast.py` exists for the module |
   | SK-DOC-001 | Docstring uses Google-style `Args:` instead of numpydoc `Parameters` |

5. **Pass criteria:** the agent names the rule and at least the SK-D-001,
   SK-F-001, and SK-I-001 violations (the three most visually obvious), ideally
   all five. If it does, the centerpiece is verified — record the result on
   bead `8ut.3`.

6. **If it underwhelms** (misses violations or doesn't cite the rule): do NOT
   improvise live. Pivot immediately to the fallback below. Also try
   re-running with the explicit `@scikit-image-conventions` mention, which
   force-attaches the rule.

## Deterministic fallback (always works)

Run in the terminal — this is 100% deterministic and never fails:

```bash
ob check examples/bad-first-contrib
```

It prints the same five `SK-*` violations in a Rich table. Narration:

> "Whether or not the model cooperates live, the rule set is deterministic —
> here's the exact same five violations from the CLI, and this is what runs
> in CI. The editor experience is the cherry on top; the guarantee is the
> engine."

This fallback is already Section 1's documented safety net in docs/demo.md.

## Why this design de-risks the moment

The catch has two independent paths to success: the Cursor agent (impressive
but probabilistic) and the CLI (deterministic). The rule and the CLI share the
same `SK-*` IDs and the same profile YAML, so the story — "one source of truth,
enforced in the editor and in CI" — holds even if the live model response is
weak. You can never be left with nothing on screen.
