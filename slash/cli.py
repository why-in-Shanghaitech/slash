import sys
import os
import shlex
import warnings
from slash import Slash
from slash.core import (
    initialize,
    shell
)
from pathlib import Path
import argparse

def get_create_parser():
    """
    Parser for the `slash create` command.
    """
    parser = argparse.ArgumentParser(prog='slash create', description='Create a new Slash environment')
    parser.add_argument('-n', '--name', help='The name of the environment', required=True)
    parser.add_argument('-f', '--file', default=None, nargs='+', help='The subscriptions to the environment. It can be a path to the config file or a URL. You can specify multiple subscriptions and all these should point to the same config files. If None, an empty config file will be created.')

    return parser

def get_remove_parser():
    """
    Parser for the `slash remove` command.
    """
    parser = argparse.ArgumentParser(prog='slash remove', description='Remove a Slash environment')
    parser.add_argument('-n', '--name', help='The name of the environment')

    return parser

def main(*args, **kwargs):

    if len(sys.argv) < 2:
        print("Usage: slash [run|activate|deactivate|create|remove] [args]")
        sys.exit(1)

    slash_exe = Path(sys.argv[0]).resolve()
    command = sys.argv[1]

    if command == "run":
        with Slash():
            os.system(shlex.join(sys.argv[2:]))
    
    elif command == "init":
        initialize(slash_exe)

    elif command == "shell":
        if len(sys.argv) < 3:
            print("Usage: slash shell [command]")
            sys.exit(1)

        if sys.argv[2] == "hook":
            print(shell.hook(slash_exe))

        elif sys.argv[2] == "activate":
            if len(sys.argv) == 3:
                env_name = 'default'
            elif len(sys.argv) == 4:
                env_name = sys.argv[3]
            else:
                print("Slash only accepts one argument for `activate`.")
                sys.exit(1)
            service = Slash(env_name).launch("slash")
            port = service.port
            if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
                warnings.warn("http_proxy is already set. It will be overwritten.")
            script = shell.activate(env_name, port)
            print(script)

        elif sys.argv[2] == "deactivate":
            env_name = os.environ.get("SLASH_ENV", None)
            if env_name is None:
                print("No environment is activated.")
                sys.exit(1)
            Slash(env_name).stop("slash")
            script = shell.deactivate()
            print(script)
        
        else:
            print("Usage: slash shell [activate|deactivate]")
            sys.exit(1)
        
    elif command == "activate":
        print("You haven't run `slash init` yet. Run `slash init` first.")

    elif command == "deactivate":
        print("You haven't run `slash init` yet. Run `slash init` first.")
    
    elif command == "create":
        from slash.core import EnvsManager
        parser = get_create_parser()
        args = parser.parse_args(sys.argv[2:])
        manager = EnvsManager()
        env = manager.create_env(args.name, args.file)
    
    elif command == "remove":
        from slash.core import EnvsManager
        parser = get_remove_parser()
        args = parser.parse_args(sys.argv[2:])
        manager = EnvsManager()
        manager.remove_env(args.name)
    
    else:
        with Slash():
            os.system(shlex.join(sys.argv[1:]))

