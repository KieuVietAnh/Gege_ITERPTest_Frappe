#!/usr/bin/env bash
set -euo pipefail
bench --site orders.localhost set-config allow_tests true
trap 'bench --site orders.localhost set-config allow_tests false' EXIT
bench --site orders.localhost run-tests --app order_management
node apps/order_management/tests/simple-order-form.test.cjs
env/bin/python -m unittest discover -s apps/order_management/tests -p 'test_docker_initialize.py'
