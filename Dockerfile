FROM frappe/build:version-15@sha256:a34e17255c5866922cb31f5e1176e22d5337b7da937db2c6a1ae56cddd6d76a5 AS builder

USER frappe
RUN bench init --frappe-branch v15.126.1 --skip-assets --no-procfile \
    --no-backups --skip-redis-config-generation /home/frappe/frappe-bench
WORKDIR /home/frappe/frappe-bench
COPY --chown=frappe:0 pyproject.toml README.md apps/order_management/
COPY --chown=frappe:0 order_management apps/order_management/order_management
COPY --chown=frappe:0 tests/simple-order-form.test.cjs apps/order_management/tests/simple-order-form.test.cjs
COPY --chown=frappe:0 tests/test_docker_initialize.py apps/order_management/tests/test_docker_initialize.py
RUN env/bin/pip install --no-cache-dir --no-deps -e apps/order_management \
    && printf 'frappe\norder_management\n' > sites/apps.txt \
    && bench build \
    && cp -a sites/assets assets \
    && rm -rf sites/assets

FROM frappe/base:version-15@sha256:322d60702547aba32afd5b961527623215bd2134ef04913125b86d72bea1a305
LABEL org.opencontainers.image.source="https://github.com/KieuVietAnh/Gege_ITERPTest_Frappe"
USER frappe
WORKDIR /home/frappe/frappe-bench
COPY --from=builder --chown=frappe:0 /home/frappe/frappe-bench /home/frappe/frappe-bench
COPY --chown=frappe:0 docker apps/order_management/docker
CMD ["bash", "apps/order_management/docker/web.sh"]
