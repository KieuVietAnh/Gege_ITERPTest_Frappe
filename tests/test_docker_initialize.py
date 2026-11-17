import importlib.util
import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import call, patch

SPEC = importlib.util.spec_from_file_location(
    "initialize", Path(__file__).resolve().parents[1] / "docker" / "initialize.py"
)
initialize = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(initialize)


class InitializeTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        previous = Path.cwd()
        os.chdir(self.directory.name)
        self.addCleanup(os.chdir, previous)
        Path("assets").mkdir()

    def test_new_site_then_restart_preserves_site_and_custom_config(self):
        with patch.dict(os.environ, DB_ROOT_PASSWORD="test-db", ADMIN_PASSWORD="test-admin"):
            with patch.object(initialize, "bench") as bench:
                initialize.main()
                self.assertEqual(bench.call_args_list[0].args[:2], ("new-site", initialize.SITE))

            site = Path("sites") / initialize.SITE
            site.mkdir()
            site_config = site / "site_config.json"
            site_config.write_text('{"db_name":"existing-database"}')
            common = Path("sites/common_site_config.json")
            config = json.loads(common.read_text())
            config["custom_setting"] = "keep"
            common.write_text(json.dumps(config))

            with patch.object(initialize, "bench") as bench:
                initialize.main()
                self.assertFalse(any(item.args[0] == "new-site" for item in bench.call_args_list))
                self.assertIn(call("--site", initialize.SITE, "migrate"), bench.call_args_list)
            self.assertEqual(json.loads(site_config.read_text())["db_name"], "existing-database")
            self.assertEqual(json.loads(common.read_text())["custom_setting"], "keep")

    def test_existing_assets_directory_is_never_replaced(self):
        Path("sites/assets").mkdir(parents=True)
        marker = Path("sites/assets/keep.txt")
        marker.write_text("keep")
        with patch.object(initialize, "bench") as bench:
            with self.assertRaisesRegex(RuntimeError, "refusing to replace"):
                initialize.main()
            bench.assert_not_called()
        self.assertEqual(marker.read_text(), "keep")



if __name__ == "__main__":
    unittest.main()
