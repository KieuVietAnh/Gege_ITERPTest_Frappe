#!/usr/bin/env bash
set -euo pipefail
exec env/bin/gunicorn \
    --chdir=sites --bind=0.0.0.0:8000 --threads=4 --workers=2 \
    --worker-class=gthread --worker-tmp-dir=/dev/shm --timeout=120 \
    frappe.app:application
