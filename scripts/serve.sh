#!/usr/bin/env bash
set -euo pipefail
export PATH="$HOME/.local/share/orders-tools/bin:/usr/local/bin:$PATH"
project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$HOME/frappe-bench"
exec bench start --procfile "$project_dir/Procfile.dev"
