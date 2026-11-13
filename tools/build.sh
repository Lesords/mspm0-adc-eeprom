#!/usr/bin/env bash
# BBW2 PCU firmware one-shot build: toolchain check + make + txt->bin + LUT verify
# Usage: tools/build.sh          (produces flash-ready pcu_pocketbeagle2.bin)
# Toolchain lives in ~/toolSpace (persistent); override with TOOL_DIR=... if elsewhere.
set -euo pipefail
cd "$(dirname "$0")/.."

TOOLCHAIN="${TOOL_DIR:-$HOME/toolSpace/ti-cgt-armllvm_4.0.4.LTS}"

if [ ! -x "$TOOLCHAIN/bin/tiarmclang" ]; then
	echo "TI ARM CLANG not found: $TOOLCHAIN" >&2
	echo "Install once (about 231 MB, unattended):" >&2
	echo "  curl -L -o /tmp/ti_installer.bin \\" >&2
	echo "    'https://dr-download.ti.com/software-development/ide-configuration-compiler-or-debugger/MD-ayxs93eZNN/4.0.4.LTS/ti_cgt_armllvm_4.0.4.LTS_linux-x64_installer.bin'" >&2
	echo "  chmod +x /tmp/ti_installer.bin && /tmp/ti_installer.bin --mode unattended --prefix ~/toolSpace" >&2
	exit 1
fi

make TOOL_DIR="$TOOLCHAIN"
python3 tools/txt2bin.py pcu_pocketbeagle2.txt
