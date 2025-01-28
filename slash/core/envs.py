import json
import secrets
import shutil
import subprocess
import sys
import tarfile
import tempfile
import time
from pathlib import Path
from typing import Dict, List, Optional, Union

from ruamel.yaml import YAML, YAMLError

import slash.utils as utils
from slash.core.config import SlashConfig
from slash.core.constants import ENVS_DIR, WORK_DIR


logger = utils.logger
yaml = YAML()

def convert(sub: Union[str, Path], tgt: Path) -> Path:
    """
    Convert the subscription to a config file.

    Arguments:
        sub: str
            The subscription URL, or path to the config file.
        tgt: Path
            The target path to save the converted subscription.
    """

    # prepare subconverter
    tar_path = WORK_DIR / "subconverter.tar.gz"

    if not tar_path.exists(): # download and cache

        logger.info("Preparing subconverter. Please wait, it could take a few minutes...")
        WORK_DIR.mkdir(parents=True, exist_ok=True)

        # Use the release
        utils.download_file(
            urls = "https://github.com/MetaCubeX/subconverter/releases/download/Alpha/subconverter_linux64.tar.gz",
            path = tar_path,
            desc = "Downloading subconverter tarball..."
        )

    # process in the temp directory
    with tempfile.TemporaryDirectory() as tmpdir:

        tpl_config = Path(tmpdir) / "ACL4SSR_Online_Mannix.ini"

        # download the latest config file
        utils.download_file(
            urls = "https://raw.githubusercontent.com/zsokami/ACL4SSR/main/ACL4SSR_Online_Mannix.ini",
            path = tpl_config,
            desc = "Downloading template config file..."
        )

        # extract the tarball
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(tmpdir, filter=lambda *args: args[0])

        # find the executable
        work_dir = Path(tmpdir) / "subconverter"
        executable = work_dir / "subconverter"

        # check if the executable exists
        if not executable.exists():
            raise FileNotFoundError("Subconverter executable not found.")

        # setup the config
        config = work_dir / "generate.ini"
        with open(config, "w") as f:
            f.write(
                utils.dals(
                    """
                    [test]
                    path=output.yaml
                    target=clash
                    insert=false
                    new_name=true
                    config=%(tpl_config)s
                    url=%(sub)s
                    """ % {"sub": str(sub), "tpl_config": str(tpl_config)}
                )
            )

        # run the executable
        result = subprocess.run([str(executable), "-g"], cwd=work_dir, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        if result.returncode != 0:
            raise ValueError("Failed to convert the subscription.")

        # move the file
        shutil.move(work_dir / "output.yaml", tgt)

    return tgt

class Env:
    def __init__(
        self,
        name: str,
        subscriptions: Optional[List[str]] = None,
        last_updated: Optional[str] = None
    ):
        """
        Create an environment object.

        Arguments:
            name: str
                The name of the environment. The only identifier to this environment.
            subscriptions: Optional[List[str]]
                The subscriptions to the environment. It can be a path to the config file or a URL. You can specify multiple subscriptions and all these should point to the same config files. If None, an empty config file will be created.
            last_updated: Optional[str]
                The last time the subscription was updated.
        """
        self.name = name
        self.subscriptions = subscriptions
        self.last_updated = last_updated

    @property
    def workdir(self) -> Path:
        return ENVS_DIR / self.name

    def save(self, path: Path = None) -> None:
        """
        Save the environment.
        """
        if path is None:
            path = self.workdir

        path.mkdir(parents=True, exist_ok=True)
        self.save_to(path / "env.json")

    def save_to(self, path: Path) -> None:
        """
        Save as a json file.
        """
        with open(path, 'w') as f:
            json.dump(vars(self), f)

    @classmethod
    def load_from(cls, path: Path) -> 'Env':
        """
        Load from a json file.
        """
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)

    def destory(self) -> None:
        """
        Destory the environment.
        """
        shutil.rmtree(self.workdir, ignore_errors=True)

    def update(self, workdir: Path = None) -> bool:
        """
        Update the environment.
        It is okay if the update fails, as the environment will automatically update if the config file is not found when activated, or we can still use the old config file if the config file already exists.

        Returns:
            is_updated: bool
                Whether the update is successful.
        """
        if workdir is None:
            workdir = self.workdir
        workdir.mkdir(parents=True, exist_ok=True)

        try:
            if self.subscriptions:
                # download the subscription
                utils.download_file(
                    urls = self.subscriptions,
                    path = workdir / "config.yaml.tmp",
                    desc = "Downloading subscription..."
                )

                # convert the subscription
                convert(workdir / "config.yaml.tmp", workdir / "config.yaml")

                # remove the temp file
                (workdir / "config.yaml.tmp").unlink()

                # download geoip.metadb
                utils.download_file(
                    urls = [
                        "https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/geoip.metadb",
                        "https://github.com/MetaCubeX/meta-rules-dat/blob/release/geoip.metadb",
                    ],
                    path = workdir / "geoip.metadb",
                    desc = "Downloading geoip.metadb..."
                )

            else:
                # create an empty subscription file
                with open(workdir / "config.yaml", 'w') as f:
                    yaml.dump({
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
                    }, f)

            self.last_updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            self.save(workdir)
            return True

        except Exception as e:
            logger.error(f"Failed to update the config file of environment '{self.name}': ({e.__class__.__name__}) {e}")
            return False

    def _get_config(self) -> dict:
        """
        Get the subscription config content.

        The config file will be parsed into a python object.
        """
        config_path = self.workdir / "config.yaml"

        def load_from(path: Path) -> dict:
            with open(path, "r") as f:
                content = yaml.load(f)
            return {} if content is None else content

        # if the file is not found or corrupted, try to update it
        try:
            return load_from(config_path)
        except (FileNotFoundError, YAMLError):
            if not self.update():
                # still error in processing the script, throw an error.
                raise FileNotFoundError("The config file is not found or corrupted, we also failed to update it.")

        # try to load the file again, this time raise an error if it still fails
        return load_from(config_path)

    def _set_config(self, content: dict):
        """
        Set the subscription config content.
        """
        config_path = self.workdir / "config.yaml"

        with open(config_path, "w") as f:
            yaml.dump(content, f)

    def set_port(self, port: int = 7890):
        """
        Set the port of the environment.
        """
        config = self._get_config()
        # properly set the port
        if 'port' in config:
            del config['port']
        if 'socks-port' in config:
            del config['socks-port']
        if 'redir-port' in config:
            del config['redir-port']
        if 'tproxy-port' in config:
            del config['tproxy-port']
        if 'mixed-port' in config:
            del config['mixed-port']

        config['port'] = int(port)
        self._set_config(config)

    def set_controller(
        self,
        port: Optional[int] = None,
        ui_folder: Optional[Union[str, Path]] = None,
        local_only: bool = False,
        secret: Optional[str] = None
    ) -> str:
        """
        Set the controller of the environment.

        Arguments:
            port: Optional[int]
                The port of the controller. If None, the controller will be disabled.
            ui_folder: Optional[Union[str, Path]]
                The folder of the UI. If None, the UI will be disabled.
            local_only: bool
                Whether the controller is only accessible from the local machine.
            secret: Optional[str]
                The secret key of the controller. If None, a new secret key will be generated.

        Returns:
            secret: str
                The secret key of the controller. If the controller is disabled, it will return an empty string.
        """
        config = self._get_config()
        # properly set the controller
        if 'external-controller' in config:
            del config['external-controller']
        if 'external-ui' in config:
            del config['external-ui']
        if 'secret' in config:
            del config['secret']

        # if port is None, disable the controller
        if port is None:
            self._set_config(config)
            return ""

        # set proper ip
        ip = "127.0.0.1" if local_only else "0.0.0.0"
        secret = secret or secrets.token_urlsafe()
        config['external-controller'] = f"{ip}:{port}"
        config['secret'] = secret

        # if ui_folder is None, disable the UI
        if not ui_folder:
            self._set_config(config)
            return secret

        # set the UI
        if isinstance(ui_folder, Path):
            ui_folder = ui_folder.resolve()
        config['external-ui'] = str(ui_folder)
        self._set_config(config)

        return secret

    def set_dialer_proxy(self, config: SlashConfig) -> bool:
        """
        Set the dialer proxy of the environment.
        """
        if config.http_server is None:
            return False

        _config = self._get_config()
        if "proxies" not in _config:
            _config["proxies"] = []
        if "proxy-groups" not in _config:
            _config["proxy-groups"] = []

        # Step 1: set the http proxy
        #         add a proxy "direct" to the config file
        proxy = {
            "name": "direct",
            "type": "http",
            "server": config.http_server,
        }
        if config.http_port is not None:
            proxy["port"] = config.http_port

        # Step 2: set the proxy
        #         add the proxy to the config file
        for idx in range(len(_config["proxies"])):
            if _config["proxies"][idx]["name"] == "direct":
                _config["proxies"][idx] = proxy
                break
        else:
            _config["proxies"].append(proxy)

        # Step 3: setup the proxy group
        #         add the proxy group "direct-group" to the config file
        if not any(pg["name"] == "direct-group" for pg in _config["proxy-groups"]):
            _config["proxy-groups"].append({
                "name": "direct-group",
                "type": "select",
                "proxies": ["direct"]
            })

        # Step 4: add dialer to all other proxies
        for p in _config["proxies"]:
            if p["name"] != "direct":
                p["dialer-proxy"] = "direct-group"

        # Step 5: replace all direct in proxy groups
        for pg in _config["proxy-groups"]:
            if "proxies" in pg:
                pg["proxies"] = [p if p != "DIRECT" else "direct" for p in pg["proxies"]]
        self._set_config(_config)

        return True


class EnvsManager:

    def __init__(self):
        # check default envs
        if "base" not in self.envs:
            self.create_env("base")

    @property
    def envs(self) -> Dict[str, Env]:
        """
        Get all environments. Hot reload from disk.
        """
        envs: Dict[str, Env] = {}

        # load envs from disk
        ENVS_DIR.mkdir(parents=True, exist_ok=True)
        for env_folder in ENVS_DIR.iterdir():
            env_file = env_folder / "env.json"
            env = Env.load_from(env_file)
            envs[env.name] = env

        return envs

    def create_env(self, *args, **kwargs) -> Env:
        """
        Create a new environment.

        Arguments:
            name: str
                The name of the environment.
            subscriptions: List[str]
                The subscriptions to the environment. It can be a path to the config file or a URL. You can specify multiple subscriptions and all these should point to the same config files. If None, an empty config file will be created.

        Returns:
            env: Env
                The created environment.
        """
        env = Env(*args, **kwargs)
        if env.name in self.envs:
            raise ValueError(f"Environment '{env.name}' already exists.")

        # process in the temp directory
        with tempfile.TemporaryDirectory() as tmpdir:
            workdir = Path(tmpdir)

            # download the subscription
            succ = env.update(workdir)

            if not succ:
                logger.error(f"Failed to create the environment '{env.name}'.")
                return None

            # move the file
            shutil.move(workdir, env.workdir)

            # print the message
            logger.info(f"environment location: {env.workdir}")
            messages = [
                "#",
                "# To activate this environment, use",
                "#",
                f"#     $ slash activate {env.name}",
                "#",
                "# To deactivate this environment, use",
                "#",
                "#     $ slash deactivate",
                ""
            ]
            for message in messages:
                logger.info(message)

        return env

    def remove_env(self, name: str):
        if name not in self.envs:
            logger.error(f"Environment '{name}' not found.")
            sys.exit(1)

        if name == "base":
            logger.error(f"Cannot remove the default environment '{name}'.")
            sys.exit(1)

        self.envs.get(name).destory()
        logger.info(f"Environment '{name}' has been removed.")

    def get_env(self, name):
        return self.envs.get(name)

    def get_envs(self):
        return self.envs

