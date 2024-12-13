from typing import Dict, Any
from collections import OrderedDict
from pathlib import Path
import re
import os
import random
from slash.core import Env, EnvsManager, ServiceManager, Service
import slash.utils as utils

logger = utils.logger


class Dispatcher:
    """
    The abstract class of service dispatcher. The only thing it does is to build the job string from
    an identifier. The ServiceManager will call the validate method to automatically remove the dead jobs.
    """
    def build(self, id_: Any) -> str:
        """
        Build the job string through an identifier.
        """
        raise NotImplementedError

    def validate(self, service: Service, job: str) -> bool:
        """
        Validate the existence of a job.

        When ServiceManager is initalized, it will examine all the jobs by calling the validate method.
        If the job is not valid, it will be removed from the service.
        """
        raise NotImplementedError


class ShellDispatcher(Dispatcher):
    """
    A shell dispatcher that uses the shell comment to distinguish the jobs. The identifier will be
    the pid of the process. If the job is dead, it will be removed.
    """
    def build(self, id_: int) -> str:
        return f"__pid_{id_}_shell__"
    
    def validate(self, service: Service, job: str) -> bool:
        match = re.match(r"^__pid_(?P<pid>\d+)_shell__$", job)
        if not match: # this is not a shell job, bypass the validation
            return True
        
        is_valid = (Path('/proc') / match.group("pid")).exists()
        if not is_valid:
            logger.warn(f"Job {job} of env '{service.env.name}' is dead. Forgot to run `slash deactivate` in other shells?")

        return is_valid


class WithStatementDispatcher(Dispatcher):
    """
    Used when the service is launched with a `with` statement. The job will be removed when the `with`
    statement is exited.
    """
    def build(self, id_: str) -> str:
        return f"__pid_{os.getpid()}_with_{id_}__"

    def validate(self, service: Service, job: str) -> bool:
        match = re.match(r"^__pid_(?P<pid>\d+)_with_(?P<salt>\w+)__$", job)
        if not match: # this is not a multi job, bypass the validation
            return True
        
        is_valid = (Path('/proc') / match.group("pid")).exists()
        if not is_valid:
            logger.warn(f"Job {job} of env '{service.env.name}' is dead.")

        return is_valid


DISPATCHERS = OrderedDict(
    [
        ("shell", ShellDispatcher()),
        ("with", WithStatementDispatcher()),
    ]
)


class Slash:
    def __init__(self, env_name: str = 'default') -> None:
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)
        self.env = self.envs_manager.get_env(env_name)

        # for the with statement
        self.salt = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))

        self.validate()

    def validate(self) -> None:
        """
        Check if there are dead jobs. If so, remove them.
        """
        services = list(self.service_manager.services.values())
        for service in services:
            for job in service.jobs:
                for dispatcher in DISPATCHERS.values():
                    if not dispatcher.validate(service, job):
                        self.stop(service.env, job)

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
        """
        return self.env.update()
    
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
        service = self.launch(DISPATCHERS['with'].build(self.salt))
        self._old_envs = (os.environ.get('http_proxy', None), os.environ.get('https_proxy', None))
        os.environ['http_proxy'] = f"http://127.0.0.1:{service.port}"
        os.environ['https_proxy'] = f"http://127.0.0.1:{service.port}"
        return self
 
    def __exit__(self, type, value, trace) -> None:
        self.stop(DISPATCHERS['with'].build(self.salt))
        if self._old_envs[0] is not None:
            os.environ['http_proxy'] = self._old_envs[0]
            os.environ['https_proxy'] = self._old_envs[1]
        else:
            del os.environ['http_proxy']
            del os.environ['https_proxy']
        return
