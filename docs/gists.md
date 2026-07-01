# Shared Gist Registry

Live, cross-machine viewer links for self-contained HTML artifacts. These are
**secret GitHub gists** (unlisted, viewable by URL — not private; don't put
secrets in them). They let us view/iterate on the artifacts from any machine
without committing the HTML into the repo.

## The one rule that keeps this lossless

**The gist ID is the shared source of truth.** To change an artifact that
already has a gist, EDIT it by ID (`gh gist edit <id> <file>`). Never create a
new gist for an artifact that's already listed — that forks the URL and loses
the shared history. Only `gh gist create` for a file not yet in this registry.

After creating a new gist, add it here and commit — that's how the other
machine learns about it (this file syncs over normal `git pull`/`push`).

## Registry

| Artifact | View (renders live) | Edit / sync |
|---|---|---|
| `docs/architecture-slides.html` | https://gistpreview.github.io/?bef9aff82a7398dff060d532208e9b2a | `gh gist edit bef9aff82a7398dff060d532208e9b2a docs/architecture-slides.html` |
| `docs/onboarding.html` | https://gistpreview.github.io/?e94aa9843bd014f9fffccffef785d7ef | `gh gist edit e94aa9843bd014f9fffccffef785d7ef docs/onboarding.html` |

## Notes per artifact

- **`architecture-slides.html`** — untracked in the repo (lives only on the
  machine that created it + the gist). Prototype of the interactive slide-nav
  format; see bead `cursor-takehome-assignment-ho3`.
- **`onboarding.html`** — tracked in the repo. It has two copies: the committed
  one in `docs/` (normal git) and the gist (via `gh gist edit`). Edit both, or
  they drift.

## Adding a new artifact

1. `gh auth status` — confirm the `gist` scope is present.
2. `grep -cE '(src|href)="https?://' <file>` — should be `0` (self-contained).
3. `gh gist create <file>` — secret by default; note the ID (last URL segment).
4. Add a row to the table above with `https://gistpreview.github.io/?<id>`.
5. Commit this file and push.
