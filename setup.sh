#!/usr/bin/env bash

set -euo pipefail

if ! command -v uv >/dev/null 2>&1; then
  echo "uv not found; installing to \"$HOME/.local/bin\"" >&2
  curl -LsSf https://astral.sh/uv/install.sh | sh
  export PATH="${HOME}/.local/bin:${PATH}"
fi

uv python install 3.13

uv sync --extra dev
uv run pre-commit install
