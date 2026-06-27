"""Generate the Cursor convention rule (.mdc) from a library profile.

This is what makes the "one profile -> three surfaces" claim literally true for
the Cursor rule surface. The rule file is no longer a hand-maintained copy that
silently drifts from the YAML; it is regenerated from the profile, and CI fails
if the checked-in file diverges (see ``--check``).
"""

import argparse
import sys
from pathlib import Path

from ob.models import LibraryProfile
from ob.profile import load_profile

REPO_ROOT = Path(__file__).parent.parent.parent
DEFAULT_PROFILE = REPO_ROOT / "profiles" / "scikit-image.yaml"
DEFAULT_RULES_DIR = REPO_ROOT / ".cursor" / "rules"


def rule_output_path(profile: LibraryProfile, rules_dir: Path) -> Path:
    """Where the generated rule for this profile lives."""
    return rules_dir / f"{profile.name}-conventions.mdc"


def render_rule(profile: LibraryProfile) -> str:
    """Render the full .mdc rule content for a profile (deterministic)."""
    prefix = profile.rule_prefix
    dc = profile.docstring_convention
    tc = profile.test_conventions
    profile_ref = f"profiles/{profile.name}.yaml"
    forbidden_inline = ", ".join(f"`{path}`" for path in profile.forbidden_paths)
    required_sections = ", ".join(dc.required_sections)

    lines: list[str] = [
        "---",
        (
            f'description: "{profile.name} contribution conventions — active '
            'when editing Python files in this workspace"'
        ),
        'globs: "**/*.py"',
        "alwaysApply: false",
        "---",
        "",
        f"<!-- GENERATED FROM {profile_ref} BY scripts/render_rules.py — DO NOT EDIT.",
        "     Edit the profile YAML and re-run `python scripts/render_rules.py`.",
        "     CI fails if this file drifts from the profile. -->",
        "",
        f"# {profile.name} Contribution Conventions",
        "",
        f"These conventions are generated from `{profile_ref}` — the team-owned",
        "source of truth. When reviewing or generating code in this workspace,",
        "enforce these rules.",
        "",
        "## When asked to review a file",
        "",
        "Check the file against every rule below and report each violation using",
        "the SAME rule IDs the `ob check` CLI emits, so the editor and CI agree.",
        "",
        f"Rule IDs use this profile's `rule_prefix` (`{prefix}`):",
        "",
        (
            f"- **{prefix}-D-001 (deprecated API):** flag any import or use of a "
            'symbol listed under "Deprecated APIs" and name the replacement.'
        ),
        (
            f"- **{prefix}-F-001 (forbidden import):** flag any import from "
            f"{forbidden_inline}."
        ),
        (
            f"- **{prefix}-I-001 (TODO-only implementation):** flag functions whose "
            "body is only `pass`, a bare `...`, or a `# TODO` with no real logic."
        ),
        (
            f"- **{prefix}-T-002 (missing test):** flag a source module that has no "
            "matching test file."
        ),
        (
            f"- **{prefix}-DOC-001 (docstring):** flag docstrings that violate the "
            f"{dc.style} style or omit a required section."
        ),
        "",
        "Report each as `RULE-ID: <what> — <fix>`, then suggest the corrected code.",
        "",
        "For a deterministic second opinion, run `ob check <workspace>` in the",
        "terminal or use the MCP `check_workspace` tool for structured results.",
        "",
        "## Naming",
        "",
        f"- Functions and variables: `{profile.naming_convention}`",
    ]
    if profile.import_convention:
        lines.append(f"- Import convention: `{profile.import_convention}`")

    lines += [
        "",
        f"## Docstrings — {dc.style}",
        "",
        f"Every public function MUST have a docstring with these sections: "
        f"{required_sections}.",
    ]
    if dc.array_shape_notation:
        lines.append(
            "- Array parameters MUST use shape notation: `(M, N)`, `(M, N, 3)`, etc."
        )
    if dc.style == "numpydoc":
        lines.append(
            "- Do NOT use Google-style `Args:` / `Returns:` — this project uses "
            "numpydoc."
        )

    lines += ["", "## Approved Directories", ""]
    lines.append("New source files may only be created in these directories:")
    lines += [f"- `{d}`" for d in profile.approved_directories]

    lines += ["", "## Forbidden Paths", ""]
    lines.append("NEVER import from or write to:")
    lines += [f"- `{path}`" for path in profile.forbidden_paths]

    if profile.deprecated_apis:
        lines += ["", "## Deprecated APIs", ""]
        lines.append("Do NOT use these — suggest the replacement instead:")
        lines += [
            f"- `{dep.symbol}` → `{dep.replacement}`" for dep in profile.deprecated_apis
        ]

    lines += [
        "",
        "## Testing",
        "",
        f"- Framework: {tc.framework}",
        f"- Test file naming: `{tc.file_pattern}` in `{tc.location_pattern}`",
        f"- Run tests with: `{tc.run_command}`",
    ]
    if tc.required_patterns:
        lines.append("- Every contribution MUST include tests with:")
        lines += [f"  - {pattern}" for pattern in tc.required_patterns]

    lines += [
        "",
        "## The CLI",
        "",
        "Run `ob check <workspace>` to validate against these conventions",
        'deterministically. Run `ob scaffold --task "..."` to create a',
        "convention-compliant workspace.",
        "",
    ]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--profile",
        default=str(DEFAULT_PROFILE),
        help="Path to the library profile YAML (default: scikit-image).",
    )
    parser.add_argument(
        "--rules-dir",
        default=str(DEFAULT_RULES_DIR),
        help="Directory where the generated .mdc rule is written.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Do not write; exit 1 if the on-disk rule differs from the profile.",
    )
    args = parser.parse_args(argv)

    profile = load_profile(args.profile)
    rendered = render_rule(profile)
    out_path = rule_output_path(profile, Path(args.rules_dir))

    if args.check:
        current = out_path.read_text(encoding="utf-8") if out_path.exists() else ""
        if current != rendered:
            print(
                f"DRIFT: {out_path} is out of date with {args.profile}.\n"
                f"Run: python scripts/render_rules.py --profile {args.profile}",
                file=sys.stderr,
            )
            return 1
        print(f"OK: {out_path} matches {args.profile}")
        return 0

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(rendered, encoding="utf-8")
    print(f"Wrote {out_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
