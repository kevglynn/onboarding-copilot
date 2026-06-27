#!/usr/bin/env python
"""CLI wrapper: generate the Cursor convention rule from a library profile.

Usage:
    python scripts/render_rules.py                       # regenerate (scikit-image)
    python scripts/render_rules.py --profile profiles/diffusers.yaml
    python scripts/render_rules.py --check               # CI drift gate
"""

from ob.render_rules import main

if __name__ == "__main__":
    raise SystemExit(main())
