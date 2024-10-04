#! /usr/bin/env python
# -*- coding: utf-8 -*-

import os
import subprocess
import sys
import shlex
import warnings
from .backend import Slash

def main():
    if len(sys.argv) < 2:
        print("Usage: slash [run|activate|deactivate|config] [args]")
        sys.exit(1)

    command = sys.argv[1]

    if command == "run":
        with Slash():
            os.system(shlex.join(sys.argv[2:]))
    
    elif command == "init":
        Slash().init()

    elif command == "shell":
        if len(sys.argv) < 3:
            print("Usage: slash shell [command]")
            sys.exit(1)

        if sys.argv[2] == "hook":
            print(Slash().hook())

        elif sys.argv[2] == "activate":
            pid, port = Slash().launch_service("slash")
            if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
                warnings.warn("http_proxy is already set. It will be overwritten.")
            print(f'export http_proxy="http://127.0.0.1:{port}"')
            print(f'export https_proxy="http://127.0.0.1:{port}"')

        elif sys.argv[2] == "deactivate":
            Slash().release_service("slash")
            print(f'unset http_proxy')
            print(f'unset https_proxy')
        
        else:
            print("Usage: slash shell [activate|deactivate]")
            sys.exit(1)
        
    elif command == "activate":
        print("You haven't run `slash init` yet. Run `slash init` first.")

    elif command == "deactivate":
        print("You haven't run `slash init` yet. Run `slash init` first.")
    
    else:
        with Slash():
            os.system(shlex.join(sys.argv[1:]))
