# Deployment Guide

How to roll out the Engineering Onboarding Copilot at your organization.

## Who Does What

| Role | Responsibility |
|------|---------------|
| **Platform / DevEx team** | Authors and maintains the profile YAML. Configures CI integration. Owns the `ob` CLI packaging. |
| **Team leads / senior engineers** | Review and approve profile changes (via code review). Contribute convention knowledge. |
| **Individual contributors** | Use Cursor with the workspace configured. Zero setup beyond opening the repo. |

The key insight: ICs don't adopt a new tool — they adopt Cursor. The conventions
reach them through rules and MCP context injection automatically.

## Minimum Viable Profile

You don't need 100% coverage to start. A profile with three elements delivers
immediate value:

```yaml
name: your-library
language: python
rule_prefix: "YL"

approved_directories:
  - src/core/
  - src/utils/

forbidden_paths:
  - src/_internal/
  - src/_vendor/

deprecated_apis:
  - symbol: yourlib.old_function
    replacement: yourlib.new_function
    reason: Consolidated in v2.0
```

This catches the two most common new-hire mistakes: putting code in the wrong
place, and using APIs that are no longer supported. Add more rules as you
identify recurring review comments.

## Integration with Existing CI

The copilot is **additive**, not a replacement for your existing linting:

```yaml
# In your CI pipeline (GitHub Actions example)
- name: Standard linting
  run: ruff check . && mypy src/

- name: Convention checks (library-specific)
  run: ob check src/
```

`ruff` handles language-level style (formatting, unused imports, type errors).
`ob check` handles library-specific conventions (approved directories, deprecated
APIs, docstring completeness, test file existence). They complement each other —
different layers, no overlap.

## Rollout Sequence

### Phase 1: One team, one repo

1. Pick the team with the most onboarding pain (highest new-hire rate or
   longest review cycles)
2. Author a minimal profile from their existing contribution guide
3. Configure `.cursor/mcp.json` and the rules in the repo
4. Add `ob check` to CI as a **warning** (non-blocking) for 2 weeks
5. Promote to blocking after the team validates the rules are correct

### Phase 2: Expand within the team

6. Grow the profile: add deprecated APIs as they're discovered in reviews,
   add test patterns, refine directory keywords
7. Enable `ob scaffold` for new contributors
8. Generate role briefs in CI step summaries

### Phase 3: Multi-team rollout

9. Each team authors their own profile YAML (see Limitations §8 below for
   the composition model needed at this stage)
10. Share a base profile for org-wide conventions; teams extend with
    library-specific rules
11. Measure and report (see Success Metrics below)

## Success Metrics

Establish a baseline before rollout, then track the trend. Set your own targets
from that baseline — the direction of travel is what matters, not a headline
percentage:

| Metric | How to measure | What good looks like |
|--------|---------------|--------|
| Convention violations per PR | Count `ob check` failures in CI logs | Downward trend vs. your baseline |
| Review comment rate (nitpicks) | Tag "convention" comments in your review tool | Downward trend vs. baseline |
| Time to first merged PR (new hires) | Track from start date to first merge | Downward trend vs. baseline |
| Profile update frequency | Git log on the profile YAML | Regular updates (proves the team owns it) |

## What You'll Need from Cursor

- **Cursor Business seats** for engineers who will use the IDE integration
- The rules and MCP server activate automatically when the repo is opened
  in Cursor — no per-user configuration needed
- The CLI (`ob`) works independently of Cursor for CI and non-Cursor users

## Common Questions

**"What if we have a monorepo with multiple libraries?"**
See [Known Limitations §8](known-limitations.md) — the current architecture
supports one profile per workspace. Multi-team orgs need profile composition
(base + overlay), which is the natural next extension. For now, use separate
workspaces or run `ob check --profile <path>` with different profiles per
subdirectory in CI.

**"What if our conventions aren't written down?"**
The profile-authoring step forces you to articulate them. This is a feature,
not a bug — the process of writing the YAML surfaces disagreements and
implicit assumptions that would otherwise stay hidden. Start with what you
know (forbidden paths, deprecated APIs) and grow from there.

**"Can we use this without Cursor?"**
Yes. The CLI runs standalone. CI integration doesn't require Cursor. You lose
the creation-time prevention (rules + MCP feeding conventions into the AI
context) but keep the detection layer (deterministic checks in the terminal
and pipeline).
