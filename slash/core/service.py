from typing import Tuple, List, Dict, Union
from pathlib import Path
import gzip
import telnetlib
import os
import re
import time
import requests
import socket
import json
import tarfile
from filelock import SoftFileLock
import slash.utils as utils
from slash.core import (
    WORK_DIR,
    Env,
    EnvsManager
)

logger = utils.logger

def get_yacd_workdir() -> Path:
    """
    Return the path to the yacd workdir.
    """
    workdir = WORK_DIR / "yacd-meta"

    if not workdir.exists():

        logger.info("Preparing dashboard. Please wait, it could take a few minutes...")
        tar_path = WORK_DIR / "yacd-meta.tar.gz"

        # download and cache
        utils.download_file(
            urls = [
                "https://github.com/MetaCubeX/Yacd-meta/archive/refs/heads/gh-pages.tar.gz",
                "https://mirror.ghproxy.com/https://github.com/MetaCubeX/Yacd-meta/archive/refs/heads/gh-pages.tar.gz"
            ],
            path = tar_path,
            desc = "Downloading dashboard...",
        )

        def filter(tarinfo: tarfile.TarInfo, *args) -> tarfile.TarInfo:
            tarinfo.name = Path(tarinfo.name).relative_to("Yacd-meta-gh-pages").as_posix()
            return tarinfo

        # extract the tarball
        with tarfile.open(tar_path, "r:gz") as tar:
            tar.extractall(workdir, filter=filter)
        
        # remove the tarball
        tar_path.unlink()
    
    return workdir

def get_executable() -> Path:
    """
    Return the path to the executable. Download if not found.
    """

    # prepare mihomo executable
    exec_path = WORK_DIR / "mihomo-v1.18.1"

    if not exec_path.exists(): # download and cache

        logger.info("Preparing web environment. Please wait, it could take a few minutes...")
        WORK_DIR.mkdir(parents=True, exist_ok=True)

        # Use mihomo to support more protocols
        utils.download_file(
            urls = [
                "https://github.com/MetaCubeX/mihomo/releases/download/v1.18.1/mihomo-linux-amd64-v1.18.1.gz",
                "https://mirror.ghproxy.com/https://github.com/MetaCubeX/mihomo/releases/download/v1.18.1/mihomo-linux-amd64-v1.18.1.gz",
                "https://gitee.com/jiang-zhida/mihomo/releases/download/v1.16.0/clash.meta-linux-amd64-v1.16.0.gz" # the version on gitee is older
            ],
            path = exec_path,
            desc = "Downloading binary...",
            write_callback = lambda src, tgt: tgt.write(gzip.decompress(src.read()))
        )
        
        exec_path.chmod(mode = 484) # rwxr--r--
    
    return exec_path


class Service:
    def __init__(self, pid: int, port: int, ctl: Tuple[int, str], env: Env, jobs: List[str]) -> None:
        self.pid = pid
        self.port = port
        if ctl is not None:
            self.ctl = tuple(ctl) # (ctl_port, secret)
        self.env = env
        self.jobs = jobs
    
    def get_controller_urls(self) -> List[str]:
        """
        Return the controller urls.
        """
        if self.ctl is None:
            return []
        
        port, secret = self.ctl

        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        return [
            f'http://127.0.0.1:{port}/ui/?hostname=127.0.0.1&port={port}&secret={secret}',
            f'http://{ip_address}:{port}/ui/?hostname={ip_address}&port={port}&secret={secret}'
        ]
    
    def is_alive(self) -> bool:
        """
        Check if the service is alive.
        """
        return (Path('/proc') / str(self.pid)).exists()
    
    def is_operational(self) -> bool:
        """
        Check if the service is operational.
        """
        # 0. check if the service is alive
        if not self.is_alive():
            return False

        # 1. check that we can establish a connection
        try:
            telnetlib.Telnet("localhost", int(self.port), timeout=3)
        except ConnectionRefusedError: 
            return False

        # 2. check that the service is ready
        test_url = "https://www.baidu.com"
        original_proxy = os.environ.get("https_proxy", None)
        try:
            os.environ["https_proxy"] = f"http://127.0.0.1:{self.port}"
            r = requests.get(test_url, timeout=5)
            if r.status_code >= 500:
                return False
        except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
            return False
        finally:
            if original_proxy is not None:
                os.environ["https_proxy"] = original_proxy
            else:
                del os.environ["https_proxy"]
        
        return True
    
    def stop(self) -> None:
        """
        Stop the service.
        """
        if self.is_alive():
            utils.runbg(['kill', '-9', str(self.pid)])

            timeout = 30
            start = time.time()
            with logger.status("Waiting the service to shut down..."):
                while self.is_alive():
                    time.sleep(1)
                    if time.time() - start > timeout:
                        logger.error("Service shutdown failed.")
                        exit(1)

    @classmethod
    def launch(cls, env: Env, job: str) -> 'Service':
        """
        Launch a service and return a service object.

        Arguments:
            env: Env
                The environment object.
            job: str
                The only identifier to the job.
        """
        with utils.FreePort() as fp:
            with utils.FreePort() as fp_ctl:
                # set the port
                env.set_port(fp.port)

                # set the controller
                secret = env.set_controller(fp_ctl.port, get_yacd_workdir())

                # start the service
                pid = utils.runbg(['nohup', str(get_executable()), "-d", str(env.workdir)])
                service = cls(pid, fp.port, (fp_ctl.port, secret), env, [job])

                # wait for the service to start
                retries = 30
                interval = 5
                with logger.status("Waiting the service to be established...") as status:
                    cnt = 0
                    while not service.is_operational():
                        cnt += 1
                        if cnt < retries:
                            status.update(f"Waiting the service to be established ({cnt}/{retries})...")
                            time.sleep(interval) # wait for the service to start
                        else:
                            logger.error("Service establish failed.")
                            service.stop()
                            exit(1)
                
                # service established
                logger.info("Service established.")
                time.sleep(interval) # wait for the service to be fully operational

                # show the controller urls
                logger.info("The service dashboard is available at:", ", ".join(service.get_controller_urls()))

                return service
    
    @classmethod
    def load(cls, env: Env) -> Union['Service', None]:
        """
        Load a service from the default path.
        """
        return cls.load_from(env, env.workdir / "service.json")
    
    @classmethod
    def load_from(cls, env: Env, path: Path) -> Union['Service', None]:
        """
        Load a service from a json file.
        """
        hostname = socket.gethostname()

        with SoftFileLock(path.with_suffix(".lock")):
            data = {}

            # read the service data
            if path.exists():
                with open(path, "r") as f:
                    string = f.read()

                if string:
                    data = json.loads(string)

            # check if the service exists
            if hostname not in data:
                return None
            
            sdata = data[hostname]
            service = Service(sdata["pid"], sdata["port"], sdata["ctl"], env, sdata["jobs"])

            # check if the service is alive
            if not service.is_alive():
                return None
        
        return service
    
    def save(self) -> None:
        """
        Save the service to a json file.
        """
        self.save_to(self.env.workdir / "service.json")
    
    def save_to(self, path: Path) -> None:
        """
        Save the service to a json file.
        """
        hostname = socket.gethostname()

        with SoftFileLock(path.with_suffix(".lock")):
            data = {}

            # read the service data
            if path.exists():
                with open(path, "r") as f:
                    string = f.read()

                if string:
                    data = json.loads(string)

            # update the service data
            if self.is_alive():
                data[hostname] = {"pid": self.pid, "port": self.port, "ctl": self.ctl, "jobs": self.jobs}
            else:
                if hostname in data:
                    del data[hostname]

            # write the service data
            with open(path, "w") as f:
                json.dump(data, f)


class ServiceManager:
    def __init__(self, envs_manager: EnvsManager) -> None:
        self.services: Dict[str, Service] = {}

        # load services from disk
        for env in envs_manager.get_envs().values():
            service = Service.load(env)
            if service is not None:
                self.services[env.name] = service
        
        # check dead jobs
        self._check_dead_jobs()
    
    def _check_dead_jobs(self) -> None:
        """
        Check if there are dead jobs. If so, remove them.
        """
        pattern = r"^__pid_(?P<pid>\d+)_(?P<comment>\w+)__$"

        services = list(self.services.values())
        for service in services:
            for job in service.jobs:
                match = re.match(pattern, job)
                
                if not match:
                    continue

                if not (Path('/proc') / match.group("pid")).exists():
                    message = f"Job {job} of env '{service.env.name}' is dead."
                    if match.group("comment") == "shell":
                        message += " Forgot to run `slash deactivate` in other shells?"
                    logger.warn(message)
                    self.stop(service.env, job)
    
    def launch(self, env: Env, job: str) -> 'Service':
        """
        Launch a service and return a service object.

        Arguments:
            env: Env
                The environment object.
            jobs: List[str]
                The list of jobs to be launched.
        """
        with SoftFileLock(env.workdir / "service_manager.lock"):
            # check if the service exists
            if env.name in self.services:
                service = self.services[env.name]
                if service.is_alive():
                    service.jobs.append(job)
                    service.save()
                    return service
                
            # launch a new service
            service = Service.launch(env, job)
            self.services[env.name] = service
            service.save()
            return service
    
    def stop(self, env: Env, job: str) -> None:
        """
        Stop a service.
        """
        with SoftFileLock(env.workdir / "service_manager.lock"):
            if env.name not in self.services:
                logger.error(f"Try to stop {job} for {env.name}, but service of {env.name} not found.")
                return

            # get the service
            service = self.services[env.name]
            if not service.is_alive():
                logger.error(f"Try to stop {job} for {env.name}, but service of {env.name} not alive.")
            
            # remove the job from the service
            if job in service.jobs:
                service.jobs.remove(job)
            else:
                logger.error(f"Try to stop {job} for {env.name}, but job not found.")

            # stop the service if no jobs are running
            if len(service.jobs) == 0:
                service.stop()
                del self.services[env.name]
            service.save()
    