#!/usr/bin/env bash
# Offline installer for spiderswitch (air-gapped / intranet usage).
# spiderswitch 离线安装脚本（内网/隔离环境）。

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

SPIDERSWITCH_HOME="${SPIDERSWITCH_HOME:-$HOME/.spiderswitch}"
VENV_DIR="$SPIDERSWITCH_HOME/venv"
BIN_DIR="$HOME/.local/bin"

WHEEL_PATH="${1:-}"
if [ -z "$WHEEL_PATH" ]; then
  echo "Usage: bash scripts/install_offline.sh /path/to/spiderswitch-*.whl"
  echo "   or: bash scripts/install_offline.sh /path/to/source-directory"
  exit 1
fi

if [ ! -e "$WHEEL_PATH" ]; then
  echo "[spiderswitch] offline source not found: $WHEEL_PATH"
  exit 1
fi

echo "[spiderswitch] offline install source: $WHEEL_PATH"
echo "[spiderswitch] home=$SPIDERSWITCH_HOME"
echo "[spiderswitch] creating virtual environment..."
python3 -m venv "$VENV_DIR"

echo "[spiderswitch] upgrading pip..."
"$VENV_DIR/bin/python" -m pip install -U pip

if [ -d "$WHEEL_PATH" ]; then
  echo "[spiderswitch] installing from local directory..."
  "$VENV_DIR/bin/pip" install "$WHEEL_PATH"
else
  echo "[spiderswitch] installing from local wheel..."
  "$VENV_DIR/bin/pip" install "$WHEEL_PATH"
fi

mkdir -p "$BIN_DIR"
ln -sf "$VENV_DIR/bin/spiderswitch" "$BIN_DIR/spiderswitch"

echo "[spiderswitch] offline installation complete."
echo "[spiderswitch] linked command: $BIN_DIR/spiderswitch"
echo "[spiderswitch] running basic doctor..."
"$VENV_DIR/bin/spiderswitch" doctor --json --no-runtime-probe || true

echo ""
echo "Next:"
echo "1) Add $BIN_DIR to PATH if needed."
echo "2) Run: spiderswitch init --client cursor --output ~/.cursor/mcp.spiderswitch.json --force"
echo "3) Configure AI_PROTOCOL_PATH and provider API keys."
