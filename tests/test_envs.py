import tempfile
import time
import unittest
from pathlib import Path

from ruamel.yaml import YAML

from slash.core.config import SlashConfig
from slash.core.envs import Env

from .test_common import TesterMixin


yaml = YAML()


class TestEnv(TesterMixin, unittest.TestCase):
    def setUp(self):
        super().setUp()
        self.env = Env(
            name="test_env",
            subscriptions=["https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub"],
            last_updated="2024-12-27 00:00:00",
        )

        # ensure that we are using the temporary directory
        self.assertTrue(self._temp_dir_path in self.env.workdir.parents)

    def test_env_workdir(self):
        self.assertIsInstance(self.env.workdir, Path)

    def test_env_save(self):
        self.env.save()
        self.assertTrue((self.env.workdir / "env.json").exists())

    def test_env_save_to(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_env.json"
            self.env.save_to(path)
            self.assertTrue(path.exists())

    def test_env_load_from(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "test_env.json"
            self.env.save_to(path)
            loaded_env = Env.load_from(path)
            self.assertIsInstance(loaded_env, Env)
            self.assertEqual(loaded_env.name, self.env.name)
            self.assertEqual(loaded_env.subscriptions, self.env.subscriptions)
            self.assertEqual(loaded_env.last_updated, self.env.last_updated)
            self.assertEqual(loaded_env.workdir, self.env.workdir)

    def test_env_destroy(self):
        self.env.save()
        self.env.destroy()
        self.assertFalse((self.env.workdir / "env.json").exists())

    def test_env_update(self):
        start = time.localtime()
        time.sleep(1)
        self.assertTrue(self.env.update())
        end = time.localtime()
        self.assertTrue((self.env.workdir / "env.json").exists())
        self.assertTrue((self.env.workdir / "config.yaml").exists())
        last_updated = time.strptime(self.env.last_updated, "%Y-%m-%d %H:%M:%S")
        self.assertTrue(start <= last_updated <= end)

    def test_env_update_empty(self):
        env = Env(name="test_env")
        with tempfile.TemporaryDirectory() as temp_dir:
            start = time.localtime()
            time.sleep(1) # otherwise the last_updated will be the same
            self.assertTrue(env.update(Path(temp_dir)))
            end = time.localtime()
            self.assertTrue((Path(temp_dir) / "env.json").exists())
            self.assertTrue((Path(temp_dir) / "config.yaml").exists())
            with open(Path(temp_dir) / "config.yaml", "r") as f:
                content = yaml.load(f)
            self.assertDictEqual(content, {
                "proxy-groups": [
                    {
                        "name": "Select",
                        "type": "select",
                        "proxies": ["DIRECT"]
                    }
                ],
                "rules": [
                    "MATCH,Select"
                ]
            })
            last_updated = time.strptime(env.last_updated, "%Y-%m-%d %H:%M:%S")
            self.assertTrue(start <= last_updated <= end)

    def test_env_update_error(self):
        # the subscription is invalid
        env = Env(name="test_env", subscriptions=["https://raw.githubusercontent.com/Pawdroid/Free-servers/main/README.md"])
        self.assertFalse(env.update())
        self.assertFalse((env.workdir / "env.json").exists())
        self.assertFalse((env.workdir / "config.yaml").exists())
        self.assertIsNone(env.last_updated)

    def test_env_set_port(self):
        self.env.set_port(1234)
        config = self.env._get_config()
        self.assertEqual(config["port"], 1234)
        self.assertNotIn("socks-port", config)
        self.assertNotIn("redir-port", config)
        self.assertNotIn("tproxy-port", config)
        self.assertNotIn("mixed-port", config)

    def test_env_set_controller_empty(self):
        secret = self.env.set_controller(port=None)
        self.assertEqual(secret, "")
        config = self.env._get_config()
        self.assertNotIn("external-controller", config)
        self.assertNotIn("external-ui", config)
        self.assertNotIn("secret", config)

    def test_env_set_controller_external(self):
        secret = self.env.set_controller(port=23142, ui_folder="/tmp/ui", local_only=False)
        config = self.env._get_config()
        self.assertEqual(config["external-controller"], "0.0.0.0:23142")
        self.assertEqual(config["external-ui"], "/tmp/ui")
        self.assertEqual(config["secret"], secret)

    def test_env_set_controller_local(self):
        secret = self.env.set_controller(port=5678, local_only=True, secret="abc123")
        self.assertEqual(secret, "abc123")
        config = self.env._get_config()
        self.assertEqual(config["external-controller"], "127.0.0.1:5678")
        self.assertNotIn("external-ui", config)
        self.assertEqual(config["secret"], "abc123")

    def test_env_set_dialer_proxy(self):
        self.assertTrue(self.env.update())
        config = SlashConfig(http_server="172.168.1.1", http_port=1234)
        self.assertTrue(self.env.set_dialer_proxy(config))


if __name__ == "__main__":
    unittest.main()
