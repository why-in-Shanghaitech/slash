import json
import os
import re
import signal
import sys
import time
from pathlib import Path
from typing import List

import filelock

import slash.utils as utils
from slash.core import WORK_DIR, EnvsManager, ServiceManager


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

    def getid(self, job: str) -> re.Match[str]:
        """
        Get the unique identifier of the job. It will be passed to the validate method to check if the job is dead.
        If the job is beyond the control of the daemon, return None. Should be implemented by the subclass.
        """
        raise NotImplementedError

    def validate(self, match: re.Match[str]) -> bool:
        """
        Validate the existence of a job. Should be implemented by the subclass.
        """
        raise NotImplementedError

    def start(self):
        """
        Check if the daemon is running. If not, start the daemon.
        """
        # FIXME: we have a concurrency issue here. If two processes start the daemon at the same time,
        # they may both think the daemon is not running and start it. One solution is to double check
        # whether the daemon is running when setting the pid file.
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
            "from slash.daemon import ProcessDaemon; ProcessDaemon().loop({})".format(
                os.getpid()
            ),
        ]

    def getid(self, job: str) -> re.Match[str]:
        """
        Get the unique identifier of the job. It will be passed to the validate method to check if the job is dead.
        If the job is beyond the control of the daemon, return None.
        """
        return re.match(r"^__pid_(?P<pid>\d+)_(?P<comment>\w+)__$", job)

    def validate(self, match: re.Match[str]) -> bool:
        """
        Validate the existence of a job.
        """
        return (Path('/proc') / match.group("pid")).exists()
