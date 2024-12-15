from typing import Dict, List
from pathlib import Path
import re
import os
import time
import json
import filelock
import sys
import signal
from slash.core import Env, EnvsManager, ServiceManager, Service, WORK_DIR
import slash.utils as utils

logger = utils.logger


class DaemonPid:
    def __init__(self, name: str):
        self.name = name

    @property
    def deamon_pid(self) -> Path:
        return WORK_DIR / 'daemon.pid'
    
    @property
    def pid(self) -> int:
        with filelock.SoftFileLock(self.deamon_pid.with_suffix('.lock')):
            if self.deamon_pid.exists():
                with open(self.deamon_pid, 'r') as f:
                    data = json.load(f)
                return data.get(self.name, None)
            else:
                with open(self.deamon_pid, 'w') as f:
                    json.dump({}, f)
        return None
    
    @pid.setter
    def pid(self, pid: int):
        with filelock.SoftFileLock(self.deamon_pid.with_suffix('.lock')):
            with open(self.deamon_pid, 'r') as f:
                data = json.load(f)
            data[self.name] = pid
            with open(self.deamon_pid, 'w') as f:
                json.dump(data, f)

    @pid.deleter
    def pid(self):
        with filelock.SoftFileLock(self.deamon_pid.with_suffix('.lock')):
            with open(self.deamon_pid, 'r') as f:
                data = json.load(f)
            if self.name in data:
                del data[self.name]
            with open(self.deamon_pid, 'w') as f:
                json.dump(data, f)
    
    @property
    def is_running(self):
        if not (ret := self.pid is not None and (Path('/proc') / str(self.pid)).exists()):
            del self.pid
        return ret


class Daemon:
    """
    The abstract daemon class that manages the services.

    The daemon will be started when the slash object is created, it will take down the pid of the
    current process; after the process exits, the daemon will check the jobs corresponding to the
    its type (shell, with, ...) and remove the dead ones every 60 seconds. If there are no jobs left,
    the daemon will exit.
    """
    # the identifier of the daemon, should be unique
    name = None
    # the loop interval (seconds)
    interval = 60

    def __init__(self):
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)
        self.deamonpid = DaemonPid(self.name)

    def launch_command(self) -> List[str]:
        """
        Get the command to launch the daemon. Should be implemented by the subclass.
        """
        raise NotImplementedError

    def getid(self, job: str) -> str:
        """
        Get the unique identifier of the job. It will be passed to the validate method to check if the job is dead.
        If the job is beyond the control of the daemon, return None. Should be implemented by the subclass.
        """
        raise NotImplementedError

    def validate(self, jid: str) -> bool:
        """
        Validate the existence of a job. Should be implemented by the subclass.
        """
        raise NotImplementedError

    def start(self):
        """
        Check if the daemon is running. If not, start the daemon.
        """
        if self.deamonpid.is_running:
            return

        # XXX: here we use utils.runbg instead of os.fork, because using fork will inherit all the
        # memory pages of the parent process, which is not what we want. It is possible that the parent
        # process uses a lot of memory, while the daemon should be as light as possible.
        utils.runbg(self.launch_command())

    def stop(self):
        """
        Stop the daemon.
        """
        if not self.deamonpid.is_running:
            return

        os.kill(self.deamonpid.pid, signal.SIGTERM)
        while self.deamonpid.is_running:
            time.sleep(1)
        del self.deamonpid.pid

    def loop(self, ppid: int):
        """
        Check the jobs every interval seconds. The loop only starts when the parent process exits.
        """
        # take down the pid of the current process
        self.deamonpid.pid = os.getpid()

        # wait for the parent process to exit
        while (Path('/proc') / str(ppid)).exists():
            time.sleep(self.interval)

        # start the loop
        while True:
            jobs = [(service, job) for service in self.service_manager.services.values() for job in service.jobs]
            jids = [(service, job, jid) for service, job in jobs if ((jid := self.getid(job)) is not None)]

            if not jids:
                break

            for service, job, jid in jids:
                if not self.validate(jid):
                    self.service_manager.stop(service.env, job)

            time.sleep(self.interval)
        
        # remove the pid file
        del self.deamonpid.pid
        exit(0)


class ProcessDaemon(Daemon):
    """
    The process daemon that manages the jobs based on the process id.
    """
    name = 'pid'

    def launch_command(self) -> List[str]:
        """
        Get the command to launch the daemon.
        """
        return [
            sys.executable, # the python interpreter
            "-c",
            "from slash.slash import ProcessDaemon; ProcessDaemon().loop({})".format(
                os.getpid()
            ),
        ]

    def getid(self, job: str) -> str:
        """
        Get the unique identifier of the job. It will be passed to the validate method to check if the job is dead.
        If the job is beyond the control of the daemon, return None.
        """
        match = re.match(r"^__pid_(?P<pid>\d+)_(?P<comment>\w+)__$", job)
        return None if not match else match.group("pid")

    def validate(self, jid: str) -> bool:
        """
        Validate the existence of a job.
        """
        return (Path('/proc') / jid).exists()


class Slash:
    def __init__(self, env_name: str = 'default') -> None:
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)
        self.env = self.envs_manager.get_env(env_name)

        # by default we start the process daemon
        ProcessDaemon().start()

    def launch(self, job: str) -> 'Service':
        """
        Launch a job.
        """
        return self.service_manager.launch(self.env, job)
    
    def stop(self, job: str) -> None:
        """
        Stop the service.
        """
        self.service_manager.stop(self.env, job)

    def update(self) -> bool:
        """
        Update the environment.
        If the service is running, update the service as well.
        """
        service = self.service_manager.services.get(self.env.name, None)
        is_updated = self.env.update()
        if is_updated and service is not None:
            service.update()
        return is_updated
    
    def info(self) -> Dict[str, str]:
        """
        Get the environment information.
        """
        info = {
            'workdir': self.env.workdir,
            'config': self.env.workdir / 'config.yaml',
            'subscriptions': self.env.subscriptions,
            'last_updated': self.env.last_updated,
        }

        if self.service_manager.services.get(self.env.name, None) is not None:
            service = self.service_manager.services[self.env.name]
            info['service_status'] = 'Online'
            info['service_port'] = service.port
            info['service_dashboard'] = service.get_controller_urls()
        else:
            info['service_status'] = 'Offline'
        
        return info

    @classmethod
    def create(cls, name: str, file: str) -> None:
        """
        Create an environment.

        Arguments:
            name (str): The name of the environment.
            file (str): The path to the environment file, or the link to the subscription.
        """
        EnvsManager().create_env(name, file)
    
    @classmethod
    def remove(cls, name: str) -> None:
        """
        Remove an environment.

        Arguments:
            name (str): The name of the environment.
        """
        EnvsManager().remove_env(name)

    @classmethod
    def list(cls) -> Dict[str, 'Env']:
        """
        List all environments.
        """
        return EnvsManager().get_envs()
    
    def __enter__(self) -> 'Slash':
        service = self.launch("__pid_{pid}_with__".format(pid=os.getpid()))
        self._old_envs = (os.environ.get('http_proxy', None), os.environ.get('https_proxy', None))
        os.environ['http_proxy'] = f"http://127.0.0.1:{service.port}"
        os.environ['https_proxy'] = f"http://127.0.0.1:{service.port}"
        return self
 
    def __exit__(self, type, value, trace) -> None:
        self.stop("__pid_{pid}_with__".format(pid=os.getpid()))
        if self._old_envs[0] is not None:
            os.environ['http_proxy'] = self._old_envs[0]
            os.environ['https_proxy'] = self._old_envs[1]
        else:
            del os.environ['http_proxy']
            del os.environ['https_proxy']
        return
