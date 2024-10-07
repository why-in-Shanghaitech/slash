import os
import warnings
from slash.core import EnvsManager, ServiceManager, Service

class Slash:
    def __init__(self, env_name: str = 'default') -> None:
        self.envs_manager = EnvsManager()
        self.service_manager = ServiceManager(self.envs_manager)
        self.env = self.envs_manager.get_env(env_name)

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
        this_pid = os.getpid()
        service = self.launch(str(this_pid))
        port = service.port
        if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
            warnings.warn("http_proxy is already set. It will be overwritten.")
        os.environ['http_proxy'] = f"http://127.0.0.1:{port}"
        os.environ['https_proxy'] = f"http://127.0.0.1:{port}"
        return self
 
    def __exit__(self, type, value, trace) -> None:
        this_pid = os.getpid()
        self.stop(str(this_pid))
        del os.environ['http_proxy']
        del os.environ['https_proxy']
        return
