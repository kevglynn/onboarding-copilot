#!/usr/bin/env bash
set -euo pipefail

# setup-scikit-image-demo.sh
# Produces a fully configured scikit-image workspace for the live demo.
# Idempotent — safe to re-run. Run the night before; open the result in Cursor.

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TARGET="${1:-$HOME/scikit-image-demo}"
SKIMAGE_TAG="v0.24.0"
SKIMAGE_REPO="https://github.com/scikit-image/scikit-image.git"

echo "=== Engineering Onboarding Copilot — Demo Staging ==="
echo "  Source:  $REPO_ROOT"
echo "  Target:  $TARGET"
echo "  Tag:     $SKIMAGE_TAG"
echo ""

# --- 1. Clone scikit-image (shallow, pinned tag) ---
if [ -d "$TARGET/.git" ]; then
  echo "[1/6] scikit-image clone already exists — refreshing config only"
else
  echo "[1/6] Cloning scikit-image ($SKIMAGE_TAG, shallow)..."
  git clone --depth 1 --branch "$SKIMAGE_TAG" "$SKIMAGE_REPO" "$TARGET"
fi

# --- 2. Copy Cursor rules ---
echo "[2/6] Installing Cursor rules..."
mkdir -p "$TARGET/.cursor/rules"
RULES=(
  scikit-image-conventions.mdc
  sdlc-implementation.mdc
  sdlc-planning.mdc
  sdlc-review.mdc
  sdlc-testing.mdc
  onboarding-copilot.mdc
)
for rule in "${RULES[@]}"; do
  cp -f "$REPO_ROOT/.cursor/rules/$rule" "$TARGET/.cursor/rules/$rule"
done

# --- 3. Configure MCP server ---
echo "[3/6] Configuring MCP server..."
cat > "$TARGET/.cursor/mcp.json" << MCPEOF
{
  "mcpServers": {
    "onboarding-copilot": {
      "type": "stdio",
      "command": "uv",
      "args": [
        "run",
        "--no-sync",
        "--project",
        "$REPO_ROOT",
        "python",
        "-m",
        "ob.mcp_server"
      ],
      "env": {
        "OB_PROFILE": "$TARGET/profiles/scikit-image.yaml"
      }
    }
  }
}
MCPEOF

# --- 4. Copy profiles ---
echo "[4/7] Installing convention profiles..."
mkdir -p "$TARGET/profiles"
cp -f "$REPO_ROOT/profiles/"*.yaml "$TARGET/profiles/"

# --- 5. Plant the bad contribution ---
# Create a scoped "first-contrib" workspace inside the clone that mirrors
# the real scikit-image directory structure. ob check scans a directory
# recursively, so this keeps the check fast and targeted.
echo "[5/7] Planting bad first-contribution..."
mkdir -p "$TARGET/first-contrib/filters"
cp -f "$REPO_ROOT/examples/bad-first-contrib/filters/_local_contrast.py" \
      "$TARGET/first-contrib/filters/_local_contrast.py"

# Also place it in the real skimage tree so Cursor sees it in context
mkdir -p "$TARGET/skimage/filters"
cp -f "$REPO_ROOT/examples/bad-first-contrib/filters/_local_contrast.py" \
      "$TARGET/skimage/filters/_local_contrast.py"

# --- 6. Make ob CLI available in this workspace ---
echo "[6/7] Installing ob CLI wrapper..."
mkdir -p "$TARGET/bin"
cat > "$TARGET/bin/ob" << 'OBWRAPPER'
#!/usr/bin/env bash
# Wrapper that delegates to the ob CLI in the assignment repo's venv.
# Created by setup-scikit-image-demo.sh — do not edit.
OBWRAPPER

# Inject the actual path (not single-quoted, so it expands)
cat >> "$TARGET/bin/ob" << OBPATH
exec "$REPO_ROOT/.venv/bin/ob" "\$@"
OBPATH
chmod +x "$TARGET/bin/ob"

# --- 7. Verify ---
echo "[7/7] Verifying ob check finds violations..."
cd "$TARGET"
OB="$TARGET/bin/ob"
OB_OUTPUT=$("$OB" check --profile profiles/scikit-image.yaml first-contrib 2>&1) || true
VIOLATION_COUNT=$(echo "$OB_OUTPUT" | grep -c "SK-" || true)

if [ "$VIOLATION_COUNT" -ge 5 ]; then
  echo "  ✓ ob check reports $VIOLATION_COUNT SK-* violations (expected 5)"
else
  echo "  ✗ Expected 5 violations, got $VIOLATION_COUNT"
  echo "  Output:"
  echo "$OB_OUTPUT"
  exit 1
fi

echo ""
echo "=== Demo workspace ready ==="
echo ""
echo "  Open in Cursor:  cursor $TARGET"
echo ""
echo "  Demo commands:"
echo "    ob check --profile profiles/scikit-image.yaml first-contrib"
echo "    ob check --profile profiles/scikit-image.yaml skimage/filters/_local_contrast.py"
echo ""
echo "  Contents staged:"
echo "    .cursor/rules/   — 6 convention + SDLC rule files"
echo "    .cursor/mcp.json — onboarding-copilot MCP server"
echo "    profiles/        — scikit-image.yaml convention profile"
echo "    first-contrib/   — scoped bad contribution workspace (ob check target)"
echo "    skimage/filters/_local_contrast.py — same file in real tree (for Cursor)"
echo ""
