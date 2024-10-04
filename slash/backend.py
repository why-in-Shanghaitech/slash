from typing import List, Tuple, Optional, Union
from dataclasses import dataclass, field
from pathlib import Path
import shlex, shutil
import os, sys, subprocess
import json
from datetime import datetime
import warnings
import requests
import socket
import time
import yaml
import gzip, tempfile
from tqdm import tqdm
from filelock import SoftFileLock
from .bindport import FreePort
from . import utils
import random
import telnetlib

import logging

logger = logging.getLogger("slash")

class Slash:

    EXEC_FOLDER = '~/.cache/slash'

    def __init__(self) -> None:
        """
        Initialize the slash service.
        """
        self.exec_folder = Path(self.EXEC_FOLDER).expanduser()
        self.executable # auto download first

    @property
    def executable(self) -> Path:
        """
        Return the path to the executable. Download if not found.
        """

        # 1. prepare mihomo executable
        exec_path = self.exec_folder / "mihomo-v1.18.1"

        if not exec_path.exists(): # download and cache

            logger.info("Preparing web environment. Please wait, it could take a few minutes...")
            self.exec_folder.mkdir(parents=True, exist_ok=True)

            # Use mihomo to support more protocols
            utils.download_file(
                urls = [
                    "https://github.com/MetaCubeX/mihomo/releases/download/v1.18.1/mihomo-linux-amd64-v1.18.1.gz",
                    "https://mirror.ghproxy.com/https://github.com/MetaCubeX/mihomo/releases/download/v1.18.1/mihomo-linux-amd64-v1.18.1.gz",
                    "https://gitee.com/jiang-zhida/mihomo/releases/download/v1.16.0/clash.meta-linux-amd64-v1.16.0.gz" # the version on gitee is older
                ],
                path = exec_path,
                desc = "Download Binary",
                write_callback = lambda src, tgt: tgt.write(gzip.decompress(src.read()))
            )
            
            exec_path.chmod(mode = 484) # rwxr--r--
        

        # 2. prepare geoip and geosite
        def verify_and_download(name: str, desc: str):
            path = self.exec_folder / "mihomo" / name
            urls = [
                f"https://fastly.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/{name}",
                f"https://github.com/MetaCubeX/meta-rules-dat/releases/download/latest/{name}",
                f"https://testingcf.jsdelivr.net/gh/MetaCubeX/meta-rules-dat@release/{name}"
            ]

            if not path.exists():
                path.parent.mkdir(parents=True, exist_ok=True)
                utils.download_file(urls = urls, path = path, desc = desc)

        verify_and_download("geoip.metadb", "Download geoip")
        verify_and_download("geoip.dat", "Download geoip")
        verify_and_download("geosite.dat", "Download geosite")

        # 3. prepare subscription
        subscription_path = self.exec_folder / "mihomo" / "config.yaml"

        if not subscription_path.exists():

            subscription_path.parent.mkdir(parents=True, exist_ok=True)

            # use fastly instead of cdn
            utils.download_file(
                urls = [
                    "https://ghproxy.net/https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
                    "https://cf.ghproxy.cc/https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
                    "https://jsd.cdn.zzko.cn/gh/anaer/Sub@main/clash.yaml",
                    "https://jsd.onmicrosoft.cn/gh/anaer/Sub@main/clash.yaml",
                    "https://fastraw.ixnic.net/anaer/Sub/main/clash.yaml",
                    "https://github.moeyy.xyz/https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
                    "https://mirror.ghproxy.com/https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
                    "https://cdn.jsdelivr.us/gh/anaer/Sub@main/clash.yaml",
                    "https://fastly.jsdelivr.net/gh/anaer/Sub@main/clash.yaml",
                    "https://gcore.jsdelivr.net/gh/anaer/Sub@main/clash.yaml",
                    "https://raw.cachefly.998111.xyz/anaer/Sub/main/clash.yaml",
                    "https://raw.githubusercontent.com/anaer/Sub/main/clash.yaml",
                ],
                path = subscription_path,
                desc = "Download subscription"
            )
        
        return exec_path
    
    
    def launch_service(self, identifier: str, config_path: str = None) -> Tuple[int, int]:
        """
        Return a clash service with a tuple (pid, port).
        Register the current application.

        Arguments:
            - identifier: The only identifier of the application to use the service.
        """
        logger_path = self.exec_folder / "logger.json"
        hostname = socket.gethostname()

        # check if service already exist
        with SoftFileLock(f"{logger_path}.lock") as lock:
            data = {}
            key = hostname

            if logger_path.exists():
                # read the service data, and append the identifier.
                with open(logger_path, "r") as f:
                    string = f.read()

                if string:
                    data = json.loads(string)
            
            status = data.get(key, {"pid": -1, "port": -1, "jobs": []})

            # check if the service is still running.
            if key in data and (Path('/proc') / str(status.get("pid", -1))).exists():
                # is alive
                pid, port = status["pid"], status["port"]

                # check if the identifier is already registered
                if identifier in status.get("jobs", []):
                    # the service is already running
                    pass
                else:
                    # the service is already running, but the identifier is not registered
                    status["jobs"].append(identifier)

            else:
                # create a new service
                ## Step 1. Get a free port
                freeport = FreePort()
                port = freeport.port

                ## Step 2. Initialize the config file
                config_folder = self.exec_folder / "mihomo"
                config_folder.mkdir(parents=True, exist_ok=True)

                if config_path is None or config_path == "":
                    config_path = config_folder / "config.yaml"

                # check if the config file exists
                config_path = Path(config_path).expanduser()
                if not config_path.exists():
                    raise FileNotFoundError(f"Config file {config_path} does not exist. Please fix it in the general settings.")

                # read from the config file
                with open(config_path, 'r') as f:
                    clash_config = yaml.safe_load(f)
                
                # properly set the port
                if 'port' in clash_config:
                    del clash_config['port']
                if 'socks-port' in clash_config:
                    del clash_config['socks-port']
                if 'redir-port' in clash_config:
                    del clash_config['redir-port']
                if 'tproxy-port' in clash_config:
                    del clash_config['tproxy-port']

                clash_config['mixed-port'] = int(port)

                # write to the config file
                with open(config_folder / "config.yaml", 'w') as f:
                    yaml.dump(clash_config, f)
                
                ## Step 3. Start service
                pid = utils.runbg(['nohup', str(self.executable), "-d", str(config_folder)])

                # wait for the service to start
                retries = 30
                while not self._is_established(port):
                    retries -= 1
                    if retries > 0:
                        logger.info(f"Service not established yet. Retrying... ({retries} remaining)")
                        time.sleep(5)
                    else:
                        logger.warm("Service establish failed.")
                        utils.runbg(['kill', '-9', str(pid)])
                        freeport.release()
                        exit(1)
                logger.info("Service established.")
                freeport.release()

                status = {"pid": pid, "port": port, "jobs": [identifier]}

            # update data
            with open(logger_path, "w") as f:
                data[key] = status
                f.write(json.dumps(data))

        return pid, port


    def release_service(self, identifier: str) -> None:
        """
        Stop the clash service if no application is running.
        """
        logger_path = self.exec_folder / "logger.json"
        hostname = socket.gethostname()

        with SoftFileLock(f"{logger_path}.lock") as lock:
            data = {}
            key = hostname

            # read data
            if logger_path.exists():
                with open(logger_path, "r") as f:
                    string = f.read()

                if string:
                    data = json.loads(string)
            
            status = data.get(key, {"pid": -1, "port": -1, "jobs": []})

            # check if the service is still running.
            if key in data and (Path('/proc') / str(status.get("pid", -1))).exists():
                # is alive
                if identifier in status.get("jobs", []):
                    status["jobs"].remove(identifier)

                    if status["jobs"]:
                        with open(logger_path, "w") as f:
                            data[key] = status
                            f.write(json.dumps(data))
                    else:
                        # shut down service
                        utils.runbg(["kill", "-9", str(status["pid"])])
                        with open(logger_path, "w") as f:
                            data.pop(key)
                            f.write(json.dumps(data))
                else:
                    # it is strange that the process is not logged
                    pass
            else:
                with open(logger_path, "w") as f:
                    data.pop(key, None) # safe even if key is not in data
                    f.write(json.dumps(data))
    
    def _is_established(self, port: int) -> bool:
        """
        This is a blocked function that will wait until the service is established.
        TODO: ...
        """
        # 1. check that we can establish a connection
        try:
            telnetlib.Telnet("localhost", int(port), timeout=3)
        except ConnectionRefusedError: 
            return False

        # 2. check that the service is ready
        test_url = "https://www.baidu.com"
        original_proxy = os.environ.get("https_proxy", None)
        try:
            os.environ["https_proxy"] = f"http://127.0.0.1:{port}"
            requests.get(test_url, timeout=5)
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            return False
        finally:
            if original_proxy is not None:
                os.environ["https_proxy"] = original_proxy
            else:
                del os.environ["https_proxy"]
        
        return True
    
    def init(self):
        s = f"""
# >>> slash initialize >>>
# !! Contents within this block are managed by 'slash init' !!
__slash_setup="$('{os.path.abspath(sys.argv[0])}' 'shell' 'hook' 2> /dev/null)"
if [ $? -eq 0 ]; then
    eval "$__slash_setup"
fi
unset __slash_setup
# <<< slash initialize <<<
"""
        bashrc = Path("~/.bashrc").expanduser()
        bashrc_modified = False
        if bashrc.exists():
            with open(bashrc, 'r') as f:
                content = f.read()
            if s not in content:
                with open(bashrc, 'a') as f:
                    f.write(s)
                bashrc_modified = True
        
        if bashrc_modified:
            logger.info(f"modified      {bashrc}")
            logger.info(f"Please run `source {bashrc}` to activate the changes.")
        else:
            logger.info(f"no change     {bashrc}")
    
    def hook(self):
        s = f"""
__slash_exe() (
    "{os.path.abspath(sys.argv[0])}" "$@"
)

__slash_hashr() {{
    if [ -n "${{ZSH_VERSION:+x}}" ]; then
        \rehash
    elif [ -n "${{POSH_VERSION:+x}}" ]; then
        :  # pass
    else
        \hash -r
    fi
}}

__slash_activate() {{
    \local ask_slash
    ask_slash="$(PS1="${{PS1:-}}" __slash_exe shell "$@")" || \\return
    \eval "$ask_slash"
    __slash_hashr
}}

__slash_deactivate() {{
    \local ask_slash
    ask_slash="$(PS1="${{PS1:-}}" __slash_exe shell "$@")" || \\return
    \eval "$ask_slash"
    __slash_hashr
}}

slash() {{
    \local cmd="${{1-__missing__}}"
    case "$cmd" in
        activate)
            __slash_activate "$@"
            ;;
        deactivate)
            __slash_deactivate "$@"
            ;;
        *)
            __slash_exe "$@"
            ;;
    esac
}}
"""
        return s

    def __enter__(self):
        this_pid = os.getpid()
        pid, port = self.launch_service(str(this_pid))
        if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
            warnings.warn("http_proxy is already set. It will be overwritten.")
        os.environ['http_proxy'] = f"http://127.0.0.1:{port}"
        os.environ['https_proxy'] = f"http://127.0.0.1:{port}"
        return self
 
    def __exit__(self, type, value, trace):
        this_pid = os.getpid()
        self.release_service(str(this_pid))
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        return
    