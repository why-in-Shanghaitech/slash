import argparse
import os
import shlex
import sys
from pathlib import Path

import slash.utils as utils
from slash.core import initialize, shell
from slash.slash import Slash


logger = utils.logger

DSCP = """
Slash command line interface

Slash commands are very similar to conda commands. You can run a command with a Slash environment by using the `slash run` command. You can also create, remove, and list environments with the `slash env` command.

Quick Start:
    # Create a new environment with a subscription
    slash create -n myenv -f https://example.com/config.yaml
    # Run a command with the newly created environment
    slash run -n myenv wget huggingface.co

Advanced Usage:
    # Initialize the Slash environment, then open a new terminal
    slash init
    # (In a new terminal) Activate the environment
    slash activate myenv
    # Run a command with the environment
    wget huggingface.co
    # Deactivate the environment
    slash deactivate

    # List all environments
    slash env list
    # Remove the environment
    slash remove myenv
"""

def get_parser():
    """
    Parser for the slash command line interface.
    """
    main_parser = argparse.ArgumentParser(prog='slash', description=DSCP, formatter_class=argparse.RawDescriptionHelpFormatter)
    subparsers = main_parser.add_subparsers(title='commands', dest='command', required=True)

    # slash run
    parser_run = argparse.ArgumentParser(add_help=False, description='Run a command with a Slash environment')
    parser_run.add_argument('-n', '--name', help='The name of the environment', default='base')
    parser_run.add_argument('args', nargs=argparse.REMAINDER, help='The command to run')
    subparsers.add_parser('run', parents=[parser_run], help=parser_run.description, description=parser_run.description)

    # slash init
    parser_init = argparse.ArgumentParser(add_help=False, description='Initialize the Slash environment')
    subparsers.add_parser('init', parents=[parser_init], help=parser_init.description, description=parser_init.description)

    # slash activate
    parser_activate = argparse.ArgumentParser(add_help=False, description='Activate the Slash environment')
    parser_activate.add_argument('name', help='The name of the environment', default='base', nargs='?')
    subparsers.add_parser('activate', parents=[parser_activate], help=parser_activate.description, description=parser_activate.description)

    # slash deactivate
    parser_deactivate = argparse.ArgumentParser(add_help=False, description='Deactivate the Slash environment')
    subparsers.add_parser('deactivate', parents=[parser_deactivate], help=parser_deactivate.description, description=parser_deactivate.description)

    # slash create
    parser_create = argparse.ArgumentParser(add_help=False, description='Create a new Slash environment')
    parser_create.add_argument('-n', '--name', help='The name of the environment', required=True)
    parser_create.add_argument('-f', '--file', default=None, nargs='+', help='The subscriptions to the environment. It can be a path to the config file or a URL. You can specify multiple subscriptions and all these should point to the same config files. If None, an empty config file will be created.')
    subparsers.add_parser('create', parents=[parser_create], help=parser_create.description, description=parser_create.description)

    # slash remove
    parser_remove = argparse.ArgumentParser(add_help=False, description='Remove a Slash environment')
    parser_remove.add_argument('-n', '--name', help='The name of the environment')
    subparsers.add_parser('remove', parents=[parser_remove], help=parser_remove.description, description=parser_remove.description)


    ## shell subparsers
    parser_shell = argparse.ArgumentParser(add_help=False, description='Slash shell internal command')
    subparsers_shell = parser_shell.add_subparsers(title='shell_commands', dest='shell_command', required=True, help="Shell commands, used internally by the shell")

    # slash shell hook
    parser_hook = argparse.ArgumentParser(add_help=False, description='Hook the shell')
    subparsers_shell.add_parser('hook', parents=[parser_hook], help=parser_hook.description, description=parser_hook.description)

    # slash shell activate
    parser_activate = argparse.ArgumentParser(add_help=False, description='Activate a Slash environment')
    parser_activate.add_argument('name', help='The name of the environment', default='base', nargs='?')
    parser_activate.add_argument('--shell_pid', help=argparse.SUPPRESS, default='1')
    subparsers_shell.add_parser('activate', parents=[parser_activate], help=parser_activate.description, description=parser_activate.description)

    # slash shell deactivate
    parser_deactivate = argparse.ArgumentParser(add_help=False, description='Deactivate a Slash environment')
    parser_deactivate.add_argument('--shell_pid', help=argparse.SUPPRESS, default='1')
    subparsers_shell.add_parser('deactivate', parents=[parser_deactivate], help=parser_deactivate.description, description=parser_deactivate.description)

    subparsers.add_parser('shell', parents=[parser_shell], help=parser_shell.description, description=parser_shell.description)


    ## env subparsers
    parser_env = argparse.ArgumentParser(add_help=False, description='Slash environment command')
    subparsers_env = parser_env.add_subparsers(title='env_commands', dest='env_command', required=True, help="Environment commands, used to manage environments")

    # slash env create
    subparsers_env.add_parser('create', parents=[parser_create], help=parser_create.description, description=parser_create.description)

    # slash env remove
    subparsers_env.add_parser('remove', parents=[parser_remove], help=parser_remove.description, description=parser_remove.description)

    # slash env list
    parser_list = argparse.ArgumentParser(add_help=False, description='List all environments')
    subparsers_env.add_parser('list', parents=[parser_list], help=parser_list.description, description=parser_list.description)

    # slash env update
    parser_update = argparse.ArgumentParser(add_help=False, description='Update a Slash environment')
    parser_update.add_argument('-n', '--name', help='The name of the environment', default=None)
    subparsers_env.add_parser('update', parents=[parser_update], help=parser_update.description, description=parser_update.description)

    # slash env info
    parser_info = argparse.ArgumentParser(add_help=False, description='Show the info of a Slash environment')
    parser_info.add_argument('-n', '--name', help='The name of the environment', default=None)
    subparsers_env.add_parser('info', parents=[parser_info], help=parser_info.description, description=parser_info.description)

    subparsers.add_parser('env', parents=[parser_env], help=parser_env.description, description=parser_env.description)

    return main_parser


def main(*args, **kwargs):
    slash_exe = Path(sys.argv[0]).resolve()
    args = get_parser().parse_args()

    if args.command == "run":
        with Slash(env_name=args.name):
            os.system(shlex.join(args.args))

    elif args.command == "init":
        initialize(slash_exe)

    elif args.command == "activate":
        logger.error("You haven't run `slash init` yet. Run `slash init` first.")
        sys.exit(1)

    elif args.command == "deactivate":
        logger.error("You haven't run `slash init` yet. Run `slash init` first.")
        sys.exit(1)

    elif args.command == "create":
        Slash.create(args.name, args.file)

    elif args.command == "remove":
        Slash.remove(args.name)

    elif args.command == "shell":

        if args.shell_command == "hook":
            print(shell.hook(slash_exe))

        elif args.shell_command == "activate":
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
            job = "__pid_{pid}_shell__".format(pid=args.shell_pid)
            service = Slash(args.name).launch(job)
            scripts.append(shell.activate(args.name, service.port))
            print("\n".join(scripts))

        elif args.shell_command == "deactivate":
            cur_env = os.environ.get("SLASH_ENV", None)

            # Check if no environment is activated
            if cur_env is None:
                logger.error("No environment is activated.")
                sys.exit(1)

            # Deactivate the current environment
            job = "__pid_{pid}_shell__".format(pid=args.shell_pid)
            Slash(cur_env).stop(job)
            script = shell.deactivate()
            print(script)

    elif args.command == "env":

        if args.env_command == "create":
            Slash.create(args.name, args.file)

        elif args.env_command == "remove":
            Slash.remove(args.name)

        elif args.env_command == "list":
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

        elif args.env_command == "update":
            name = args.name if args.name is not None else os.environ.get("SLASH_ENV", None)
            if name is None:
                logger.error("No environment is activated. Please specify the environment name with the `-n` flag.")
                sys.exit(1)
            else:
                Slash(name).update()
                logger.info(f"Environment '{name}' updated.")

        elif args.env_command == "info":
            name = args.name if args.name is not None else os.environ.get("SLASH_ENV", None)
            if name is None:
                logger.error("No environment is activated. Please specify the environment name with the `-n` flag.")
                sys.exit(1)
            else:
                info = Slash(name).info()
                logger.info(f"Environment '{name}':")
                logger.info(f"         config: {info['config']}")
                logger.info(f"  subscriptions: {info['subscriptions']}")
                logger.info(f"    last update: {info['last_updated']}")
                if info["service_status"] == "Online":
                    logger.info( "        Service: [green]Online[/green]")
                    logger.info(f"           Port: {info['service_port']}")
                    logger.info(f"      Dashboard: {info['service_dashboard']}")
                else:
                    logger.info( "        Service: [red]Offline[/red]")

