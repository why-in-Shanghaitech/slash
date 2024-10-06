from typing import List, Union, Iterable
from pathlib import Path
import requests
import socket
import tempfile
import subprocess
import os
import filelock
import random
import time
from tqdm import tqdm
from textwrap import dedent
import logging

logger = logging.getLogger("slash")


class FreePort:
    def __init__(self, ports: Iterable = None, timeout: int = -1) -> None:
        """
        Bind to a free port in the given range.
        This is actually a file lock with a test bind to a port. The port is immediately released after the test.

        Arguments:
            ports (Iterable): A range of ports to choose from. The object should have __len__ and __getitem__ methods.  Default is range(20000, 30000).
            timeout (int): Wait up to this many seconds to acquire a port. Default is -1 (infinite).
        """
        self.timeout = timeout
        self.ports: Iterable = ports
        self.port: Union[int, None] = None

        if self.ports is None:
            self.ports = range(20000, 30000)
    
    @staticmethod
    def is_free(port: int) -> bool:
        """
        Check if a port is free.
        """
        try:
            sock = socket.socket()
            sock.bind(('', port))
            sock.close()
            return True
        except (PermissionError, OSError):
            return False

    def acquire(self) -> 'FreePort':
        """
        Acquire a free port.
        """
        start_time = time.time()
        while self.timeout < 0 or time.time() - start_time < self.timeout:
            port = random.choice(self.ports)

            try:
                lock = filelock.SoftFileLock(f'/tmp/slash_port_{port}.lock')
                lock.acquire(blocking=False)
            except filelock.Timeout:
                continue

            if self.is_free(port):
                self.port = port
                self.lock = lock
                return self
            else:
                lock.release()
                time.sleep(0.01)
        
        raise TimeoutError('No free port available.')
    
    def release(self) -> None:
        """
        Release the port.
        """
        if self.port is None:
            return

        self.lock.release()
        self.port = None

    def __enter__(self) -> 'FreePort':
        return self.acquire()
    
    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self.release()



def dals(string):
    """dedent and left-strip"""
    return dedent(string).lstrip()

def download_file(
    urls: Union[str, List[str]],
    path: Union[str, Path],
    desc: str = None,
    timeout: int = 15,
    write_callback = None,
):
    """
    Download a file from the internet. If the file already exists, it will skip the download.
    If the url is blocked, then try the next one.

    write_callback should be a function with the source and target file descriptors as input.
    """
    if not isinstance(urls, list):
        urls = [urls]
    
    if isinstance(path, str):
        path = Path(path)
    
    if path.exists():
        return

    for idx, url in enumerate(urls):
        try:
            logger.info(f"Attempt to download {url} to {path}, waiting up to {timeout} seconds...")
            r = requests.get(url, stream = True, timeout=timeout)
            total = int(r.headers.get('Content-Length', 0)) // 1024
            with tempfile.TemporaryFile("w+b") as tmp:
                # download to tmp dir
                for chunk in tqdm(r.iter_content(chunk_size = 1024), desc=desc, total=total, unit='KB', leave=False):
                    if chunk:
                        tmp.write(chunk)
                tmp.seek(0)
                # move to home
                with open(path, "wb") as f:
                    if write_callback:
                        write_callback(tmp, f)
                    else:
                        f.write(tmp.read())
            break
        except requests.exceptions.RequestException:
            logger.info(f"Failed to download {url}. Retrying ({idx + 1}/{len(urls)})...")
    else:
        raise requests.exceptions.RequestException("All urls are blocked.")

def runbg(command: List[str]) -> int:
    """
    Run command in the background and return a pid.
    ref: https://stackoverflow.com/questions/6011235
    """
    p = subprocess.Popen(command,
        stdout=open('/dev/null', 'w'),
        stderr=open('/dev/null', 'w'),
        preexec_fn=os.setpgrp
    )
    return p.pid
    
