import os
import random
from slash.core import EnvsManager, ServiceManager, Service
import slash.utils as utils

logger = utils.logger

class Slash:
    def __init__(self, env_name: str = 'default') -> None:
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)
        self.env = self.envs_manager.get_env(env_name)

        random_str = ''.join(random.choices('abcdefghijklmnopqrstuvwxyz', k=8))
        self._with_jobname = f"__pid_{os.getpid()}_with-{random_str}__"

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
    
    def __enter__(self) -> 'Slash':
        service = self.launch(self._with_jobname)
        if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
            logger.warn("http_proxy is already set. It will be overwritten.")
        os.environ['http_proxy'] = f"http://127.0.0.1:{service.port}"
        os.environ['https_proxy'] = f"http://127.0.0.1:{service.port}"
        return self
 
    def __exit__(self, type, value, trace) -> None:
        self.stop(self._with_jobname)
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        return
