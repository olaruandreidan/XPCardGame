#!/bin/zsh
set -eu
cd "$(dirname "$0")"
runtime="$HOME/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/bin/python3"
if [[ -x .venv/bin/python3 ]]; then
    runtime="$PWD/.venv/bin/python3"
elif [[ ! -x "$runtime" ]]; then
    runtime="$(command -v python3 || true)"
fi
if [[ -z "$runtime" ]] || ! "$runtime" -c 'import reportlab, pypdf' 2>/dev/null; then
    print 'Please install the two dependencies using the Quick start in README.md.'
    read '?Press Return to close.'
    exit 1
fi
if ! "$runtime" generate.py "$@"; then
    print 'The build failed. Your previous PDFs have been kept.'
    read '?Press Return to close.'
    exit 1
fi
open output/pdf
