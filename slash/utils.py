from typing import List, Union
from pathlib import Path
import requests
import tempfile
import subprocess
import os
from tqdm import tqdm
import logging

logger = logging.getLogger("slash")

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
    
