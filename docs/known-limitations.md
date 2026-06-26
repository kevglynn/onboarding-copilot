# Known Limitations

Honest accounting of where this artifact breaks and how each limitation
would be addressed in a real customer engagement.

## 1. Deterministic checks only — no semantic code understanding

The checker applies rule-based pattern matching against the profile
(regex for deprecated APIs, AST-level import checks, file existence
tests). It cannot understand whether code is *logically* correct, only
whether it follows structural conventions.

**In a real engagement:** Layer LLM-powered semantic review on top of
the deterministic checks — use the Cursor agent for nuanced review
while keeping the rule-based checks as the reproducible baseline.

## 2. Single-profile scope — one library at a time

The current architecture supports one profile per workspace. Monorepos
with multiple libraries (e.g., a shared `utils/` package alongside
the main library) would need multiple profiles or a profile-composition
mechanism.

**In a real engagement:** Add profile inheritance or composition —
a base profile for org-wide conventions, extended by per-library
profiles. The YAML schema already supports this with minimal changes.

## 3. Template-driven role briefs — no code-aware content

Role briefs are generated from the workspace metadata (file list,
profile rules, checklist status), not from reading and understanding
the actual source code. The PM brief says "new filter helper" because
the scaffold told it so, not because it analyzed the implementation.

**In a real engagement:** Use the Cursor agent to generate code-aware
summaries that feed into the brief templates. The template structure
stays (it ensures consistency), but the content becomes richer.

## 4. Hand-curated conventions — no automated discovery

The profile YAML is manually authored from the library's contribution
guide and style conventions. If the library changes conventions (e.g.,
deprecates an API, changes test naming), someone must update the YAML.

**In a real engagement:** Connect to the library's changelog and
deprecation warnings. Build a convention-discovery tool that parses
the contribution guide and proposes profile updates for human review.

## 5. No multi-file refactor support

The scaffold creates isolated new files. It does not handle changes
that span multiple existing files (e.g., "add this function and also
update the module's `__init__.py` to export it"). Cross-file
refactoring requires human judgment or a more sophisticated agent.

**In a real engagement:** This is where Cursor's agent mode shines —
the Cursor rules would guide multi-file changes while the CLI handles
the single-file convention checks. The profile would define which files
are "related" (e.g., `__init__.py` always needs updating when adding
a public function).

## 6. No live connection to the upstream library

The profile is a snapshot of conventions at authoring time. It does not
pull from the live scikit-image repository or track upstream changes.
The profile could drift from reality if conventions change.

**In a real engagement:** Periodic profile refresh as part of the
team's maintenance workflow. Could be automated with a CI job that
diffs the profile against the library's current contribution guide.

## 7. MCP tools — `check` is exposed; `scaffold`/`brief` are not yet

The MCP server exposes its 7 conventions as resources **and** a
`check_workspace` tool, so the Cursor agent can run the deterministic checker
itself (the same `SK-*` rule IDs as the CLI) and act on the structured results
— not just read conventions. `scaffold` and `brief` are not yet exposed as MCP
tools, so the agent still shells out to the CLI for those.

**In a real engagement:** Add MCP tool endpoints for `scaffold` and `brief`
too, so the agent can create a convention-compliant workspace and generate
role briefs autonomously — completing fully agent-driven enforcement end to
end.
