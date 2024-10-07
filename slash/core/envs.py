from typing import List, Dict, Tuple, Optional, Union
from pathlib import Path
import json
import time
import tempfile
import yaml
import shutil
import tarfile
import subprocess
import slash.utils as utils
from slash.core.constants import WORK_DIR, ENVS_DIR
import logging

logger = logging.getLogger("slash")

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
            urls = [
                "https://github.com/tindy2013/subconverter/releases/download/v0.9.0/subconverter_linux64.tar.gz",
                "https://ghproxy.net/https://github.com/tindy2013/subconverter/releases/download/v0.9.0/subconverter_linux64.tar.gz",
            ],
            path = tar_path,
            desc = "Download Tarball"
        )
    
    # process in the temp directory
    with tempfile.TemporaryDirectory() as tmpdir:

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
                    ver=4
                    url=%(sub)s
                    """ % {"sub": str(sub)}
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
    
    def save(self) -> None:
        """
        Save the environment.
        """
        self.workdir.mkdir(parents=True, exist_ok=True)
        self.save_to(self.workdir / "env.json")
    
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
    
    def update(self) -> bool:
        """
        Update the environment.
        It is okay if the update fails, as the environment will automatically update if the config file is not found when activated, or we can still use the old config file if the config file already exists.

        Returns:
            is_updated: bool
                Whether the update is successful.
        """
        try:
            if self.subscriptions:
                # TODO: check if we need to convert the subscription
                def write_callback(src, tgt):
                    tgt.write(src.read())

                # download the subscription
                utils.download_file(
                    urls = self.subscriptions,
                    path = self.workdir / "config.yaml.tmp",
                    desc = "Download subscription",
                    write_callback = write_callback
                )

                convert(self.workdir / "config.yaml.tmp", self.workdir / "config.yaml")

                # remove the temp file
                (self.workdir / "config.yaml.tmp").unlink()

            else:
                # create an empty subscription file
                with open(self.workdir / "config.yaml", 'w') as f:
                    f.write("")

            self.last_updated = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            self.save()
            return True

        except Exception as e:
            logger.error(f"Failed to update the config file of environment {self.name}: {e}")
            return False
    
    def get_config(self) -> dict:
        """
        Get the subscription config content.

        The config file will be parsed into a python object.
        """
        config_path = self.workdir / "config.yaml"

        # download the subscriptions
        if not config_path.exists():

            if not self.update():
                # still error in processing the script, throw an error.
                raise FileNotFoundError("The config file is not found.")

        content = None
        with open(config_path, "r") as f:
            content = yaml.safe_load(f)
        
        if content is None:
            content = {}
        
        return content
    
    def set_config(self, content: dict):
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
        config = self.get_config()
        # properly set the port
        if 'port' in config:
            del config['port']
        if 'socks-port' in config:
            del config['socks-port']
        if 'redir-port' in config:
            del config['redir-port']
        if 'tproxy-port' in config:
            del config['tproxy-port']

        config['mixed-port'] = int(port)
        self.set_config(config)


class EnvsManager:

    def __init__(self):
        self.envs: Dict[str, Env] = {}

        # load envs from disk
        ENVS_DIR.mkdir(parents=True, exist_ok=True)
        for env_folder in ENVS_DIR.iterdir():
            env_file = env_folder / "env.json"
            env = Env.load_from(env_file)
            self.envs[env.name] = env
        
        # check default envs
        if "base" not in self.envs:
            self.create_env("base")
        if "default" not in self.envs:
            self.create_env("default", [
                "https://proxy.v2gh.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
                "https://ghproxy.net/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
                "https://cf.ghproxy.cc/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
                "https://jsd.cdn.zzko.cn/gh/Pawdroid/Free-servers@main/sub",
                "https://jsd.onmicrosoft.cn/gh/Pawdroid/Free-servers@main/sub",
                "https://fastraw.ixnic.net/Pawdroid/Free-servers/main/sub",
                "https://github.moeyy.xyz/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
                "https://mirror.ghproxy.com/https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
                "https://cdn.jsdelivr.us/gh/Pawdroid/Free-servers@main/sub",
                "https://fastly.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub",
                "https://gcore.jsdelivr.net/gh/Pawdroid/Free-servers@main/sub",
                "https://raw.cachefly.998111.xyz/Pawdroid/Free-servers/main/sub",
                "https://raw.githubusercontent.com/Pawdroid/Free-servers/main/sub",
            ])

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
        
        # create the environment folder
        env.save()

        # download the subscription
        env.update()

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
            f"#     $ slash deactivate",
            ""
        ]
        for message in messages:
            logger.info(message)
        
        self.envs[env.name] = env
        
        return env

    def remove_env(self, name: str):
        if name not in self.envs:
            raise ValueError(f"Environment '{name}' not found.")
        
        if name in ["base", "default"]:
            raise ValueError(f"Cannot remove the default environment '{name}'.")
        
        env = self.envs.get(name)
        shutil.rmtree(env.workdir, ignore_errors=True)
        del self.envs[name]

        logger.info(f"Environment '{name}' has been removed.")

    def get_env(self, name):
        return self.envs.get(name)

    def get_envs(self):
        return self.envs

