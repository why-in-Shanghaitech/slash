import gzip
import json
import os
import socket
import sys
import tarfile
import telnetlib
import time
from pathlib import Path
from typing import Dict, List, Tuple, Union

import psutil
import requests
from filelock import SoftFileLock

import slash.utils as utils
from slash.core import WORK_DIR, ConfigManager, Env, EnvsManager


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
            urls = "https://github.com/MetaCubeX/Yacd-meta/archive/refs/heads/gh-pages.tar.gz",
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
        return utils.get_process(self.pid) is not None

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
        with utils.FreePort() as fp, utils.FreePort() as fp_ctl:
            # set the port
            env.set_port(fp.port)

            # set the controller
            secret = env.set_controller(fp_ctl.port, get_yacd_workdir())

            # possibly set the dialer proxy
            env.set_dialer_proxy(ConfigManager().get_config())

            # start the service
            pid = utils.runbg(['nohup', str(get_executable()), "-d", str(env.workdir)])
            service = cls(pid, fp.port, (fp_ctl.port, secret), env, [job])

            # wait for the service to start
            try:
                timeout = 150
                interval = 5
                launched = False
                with logger.status("Waiting the service to be established...") as status:
                    start = time.time()
                    time.sleep(interval)
                    while not service.is_operational():
                        if not service.is_alive() or (duration := time.time() - start) > timeout:
                            break
                        status.update(f"Waiting the service to be established (ETA {time.strftime('%M:%S', time.localtime(timeout - duration))})...")
                        time.sleep(interval) # wait for the service to start
                    else:
                        launched = True
            except KeyboardInterrupt:
                logger.error("Service establish interrupted.")
                service.stop()
                sys.exit(1)
            except Exception as e:
                logger.error(f"Service establish failed: {e}")
                service.stop()
                sys.exit(1)

            if not launched:
                logger.error("Service establish failed.")
                service.stop()
                sys.exit(1)

            # service established
            logger.info("Service established.")
            time.sleep(interval) # wait for the service to be fully operational

            # show the controller urls
            logger.info("The service dashboard is available at:", ", ".join(service.get_controller_urls()))

            return service

    def update(self) -> bool:
        """
        Update the service.
        """
        # if the service is not alive or not operational, do nothing
        if not self.is_alive() or not self.is_operational():
            return False

        # update the config
        port, secret = self.ctl
        self.env.set_port(self.port)
        self.env.set_controller(port, get_yacd_workdir(), secret=secret)
        self.env.set_dialer_proxy(ConfigManager().get_config())

        # update the service
        url = f'http://127.0.0.1:{port}/configs'
        headers = {
            'Content-Type': 'application/json',
            "Authorization": f"Bearer {secret}"
        }
        payload = '{"path": "", "payload": ""}'
        response = requests.put(url, headers=headers, data=payload)

        if response.status_code != 204:
            logger.warn(f"Service '{self.env.name}' update failed. The config file might have been changed, but the web service will remain unchanged.")
            return False

        logger.info(f"Service '{self.env.name}' updated.")
        return True

    def stop(self) -> None:
        """
        Stop the service.
        """
        proc = utils.get_process(self.pid)

        if proc is not None:
            proc.terminate()
            with logger.status("Waiting the service to shut down..."):
                try:
                    proc.wait(timeout=30)
                except psutil.TimeoutExpired:
                    logger.error("Service shutdown failed.")
                    exit(1)

            logger.info("Service stopped.")
        else:
            logger.warn("Try to stop a service, but the service is not alive.")

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
        self.envs_manager = envs_manager

    @property
    def services(self) -> Dict[str, Service]:
        """
        Return the services. Hot reload from disk.
        """
        services: Dict[str, Service] = {}

        # load services from disk
        for env in self.envs_manager.get_envs().values():
            service = Service.load(env)
            if service is not None:
                services[env.name] = service

        return services

    def launch(self, env: Env, job: str) -> 'Service':
        """
        Launch a service and return a service object.

        Arguments:
            env: Env
                The environment object.
            job: str
                The name of job to be launched.
        """
        with SoftFileLock(env.workdir / "service_manager.lock"):
            service = self.services.get(env.name, None)

            # if the service does not exist, launch a new one
            if service is None:
                service = Service.launch(env, job)
                service.save()
                return service

            # check if the service is alive (this should not happen)
            if not service.is_alive():
                logger.error(f"Try to launch {job} for {env.name}, but service is not alive.")
                raise ValueError(f"Service of {env.name} is not alive.")

            # check if the job is already running
            if job in service.jobs:
                logger.error(f"Try to launch {job} for {env.name}, but job is already running.")
                raise ValueError(f"Job {job} is already running.")

            # add the job to the service
            service.jobs.append(job)
            service.save()
            return service

    def stop(self, env: Env, job: str) -> None:
        """
        Stop a service.
        """
        with SoftFileLock(env.workdir / "service_manager.lock"):
            service = self.services.get(env.name, None)

            # if the service does not exist, do nothing
            if service is None:
                logger.error(f"Try to stop {job} for {env.name}, but service of {env.name} not found.")
                return

            # check if the service is alive
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
            service.save()
