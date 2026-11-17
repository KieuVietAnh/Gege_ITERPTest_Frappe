import json
import os
import subprocess
from pathlib import Path

SITE = "orders.localhost"


def bench(*args):
    subprocess.run(["bench", *args], check=True)


def main():
    sites = Path("sites")
    sites.mkdir(exist_ok=True)
    assets = sites / "assets"
    if assets.is_symlink():
        if assets.resolve() != Path.cwd() / "assets":
            raise RuntimeError("Unexpected assets link; refusing to replace it.")
    elif assets.exists():
        raise RuntimeError("Expected an assets symlink; refusing to replace existing files.")
    else:
        assets.symlink_to(Path.cwd() / "assets", target_is_directory=True)

    config_path = sites / "common_site_config.json"
    config = json.loads(config_path.read_text()) if config_path.exists() else {}
    config.update({
        "db_host": "db", "db_port": 3306,
        "redis_cache": "redis://redis-cache:6379",
        "redis_queue": "redis://redis-queue:6379",
        "redis_socketio": "redis://redis-queue:6379", "socketio_port": 9000,
    })
    temporary = config_path.with_suffix(".tmp")
    temporary.write_text(json.dumps(config), encoding="utf-8")
    temporary.replace(config_path)
    (sites / "apps.txt").write_text("frappe\norder_management\n", encoding="utf-8")

    if not (sites / SITE / "site_config.json").exists():
        bench("new-site", SITE, "--db-type", "mariadb", "--db-host", "db",
              "--db-root-username", "root", "--db-root-password", os.environ["DB_ROOT_PASSWORD"],
              "--admin-password", os.environ["ADMIN_PASSWORD"], "--mariadb-user-host-login-scope=%")

    bench("--site", SITE, "set-maintenance-mode", "on")
    bench("--site", SITE, "install-app", "order_management")
    bench("--site", SITE, "migrate")
    bench("--site", SITE, "execute", "frappe.desk.page.setup_wizard.setup_wizard.setup_complete",
          "--args", json.dumps([{
              "language": "English", "country": "Vietnam", "currency": "VND",
              "timezone": "Asia/Ho_Chi_Minh", "enable_telemetry": 0,
          }]))
    bench("--site", SITE, "enable-scheduler")
    bench("--site", SITE, "set-maintenance-mode", "off")


if __name__ == "__main__":
    main()
