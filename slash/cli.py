import sys
import os
import shlex
from pathlib import Path
import argparse

from slash import Slash
from slash.core import (
    initialize,
    shell
)
import slash.utils as utils

logger = utils.logger

def get_general_parser():
    """
    Parser for the general slash command.
    """
    parser = argparse.ArgumentParser(prog='slash', description='Slash command line interface')
    parser.add_argument('command', help='The command to run. Options: run, init, shell, activate, deactivate, create, remove. If no command is provided, it will use "run" as default.')
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')

    return parser

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

def get_shell_parser():
    """
    Parser for the shell slash command.
    """
    parser = argparse.ArgumentParser(prog='slash shell', description='Slash shell internal command')
    parser.add_argument('command', help='The command to run', choices=['hook', 'activate', 'deactivate'])
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')

    return parser

def get_shell_activate_parser():
    """
    Parser for the `slash shell activate` command.
    """
    parser = argparse.ArgumentParser(prog='slash activate', description='Activate a Slash environment')
    parser.add_argument('name', help='The name of the environment', default='default', nargs='?')
    parser.add_argument('--shell_pid', help=argparse.SUPPRESS, default='1')

    return parser

def get_shell_deactivate_parser():
    """
    Parser for the `slash shell activate` command.
    """
    parser = argparse.ArgumentParser(prog='slash deactivate', description='Deactivate a Slash environment')
    parser.add_argument('--shell_pid', help=argparse.SUPPRESS, default='1')

    return parser

def get_env_parser():
    """
    Parser for the `slash env` command.
    """
    parser = argparse.ArgumentParser(prog='slash env', description='Slash environment command')
    parser.add_argument('command', help='The command to run', choices=['create', 'remove', 'list'])
    parser.add_argument('args', nargs=argparse.REMAINDER, help='Arguments for the command')

    return parser

def get_env_create_parser():
    """
    Parser for the `slash env create` command.
    """
    parser = argparse.ArgumentParser(prog='slash env create', description='Create a new Slash environment')
    parser.add_argument('-n', '--name', help='The name of the environment', required=True)
    parser.add_argument('-f', '--file', default=None, nargs='+', help='The subscriptions to the environment. It can be a path to the config file or a URL. You can specify multiple subscriptions and all these should point to the same config files. If None, an empty config file will be created.')

    return parser

def get_env_remove_parser():
    """
    Parser for the `slash env remove` command.
    """
    parser = argparse.ArgumentParser(prog='slash env remove', description='Remove a Slash environment')
    parser.add_argument('-n', '--name', help='The name of the environment')

    return parser

def main(*args, **kwargs):
    args = get_general_parser().parse_args()

    if args.command == "run":
        with Slash():
            os.system(shlex.join(args.args))
    
    elif args.command == "init":
        slash_exe = Path(sys.argv[0]).resolve()
        initialize(slash_exe)
        
    elif args.command == "activate":
        logger.error("You haven't run `slash init` yet. Run `slash init` first.")
        sys.exit(1)

    elif args.command == "deactivate":
        logger.error("You haven't run `slash init` yet. Run `slash init` first.")
        sys.exit(1)
    
    elif args.command == "create":
        args = get_create_parser().parse_args(args.args)
        Slash.create(args.name, args.file)
    
    elif args.command == "remove":
        args = get_remove_parser().parse_args(args.args)
        Slash.remove(args.name)

    elif args.command == "shell":
        args = get_shell_parser().parse_args(args.args)

        if args.command == "hook":
            slash_exe = Path(sys.argv[0]).resolve()
            print(shell.hook(slash_exe))

        elif args.command == "activate":
            args = get_shell_activate_parser().parse_args(args.args)
            cur_env = os.environ.get("SLASH_ENV", None)
            scripts = [""]

            # Check if the environment is already activated
            if args.name == cur_env:
                return

            # Deactivate the current environment
            if cur_env is not None:
                Slash(cur_env).stop("slash")
                scripts.append(shell.deactivate())
            else:
                if 'http_proxy' in os.environ or 'https_proxy' in os.environ:
                    logger.warn("http_proxy is already set. It will be overwritten.")

            # Activate the new environment
            service = Slash(args.name).launch(f"__pid_{args.shell_pid}_shell__")
            scripts.append(shell.activate(args.name, service.port))
            print("\n".join(scripts))

        elif args.command == "deactivate":
            args = get_shell_deactivate_parser().parse_args(args.args)
            cur_env = os.environ.get("SLASH_ENV", None)

            # Check if no environment is activated
            if cur_env is None:
                logger.error("No environment is activated.")
                sys.exit(1)

            # Deactivate the current environment
            Slash(cur_env).stop(f"__pid_{args.shell_pid}_shell__")
            script = shell.deactivate()
            print(script)
    
    elif args.command == "env":
        args = get_env_parser().parse_args(sys.argv[2:])

        if args.command == "create":
            args = get_env_create_parser().parse_args(args.args)
            Slash.create(args.name, args.file)
        
        elif args.command == "remove":
            args = get_env_remove_parser().parse_args(args.args)
            Slash.remove(args.name)
        
        elif args.command == "list":
            envs = Slash.list()
            cur_env = os.environ.get("SLASH_ENV", None)
            
            s = [
                "# slash environments:",
                "#",
            ]
            for name, env in envs.items():
                if name == cur_env:
                    s.append(f"{name:<21} *  {env.workdir}")
                else:
                    s.append(f"{name:<21}    {env.workdir}")
            
            for line in s:
                logger.info(line)
    
    else:
        with Slash():
            os.system(shlex.join(sys.argv[1:]))

