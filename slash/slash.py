import os
from typing import Dict

import slash.utils as utils
from slash.core import ConfigManager, Env, EnvsManager, Service, ServiceManager
from slash.daemon import ProcessDaemon


logger = utils.logger


class Slash:
    """
    The main interface of the Slash library.
    """
    daemons = [ProcessDaemon]
    config = ConfigManager()

    def __init__(self, env_name: str = 'base') -> None:
        self.env_name = env_name
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)

        # start the daemon
        for daemon in self.daemons:
            daemon().start()

    @property
    def env(self) -> Env:
        return self.envs_manager.get_env(self.env_name)

    @property
    def service(self) -> Service:
        return self.service_manager.services.get(self.env_name, None)

    def launch(self, job: str) -> Service:
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
        is_updated = self.env.update()
        if is_updated and (service := self.service) is not None:
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

        if (service := self.service) is not None:
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
