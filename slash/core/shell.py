import json
import os
import re
import shlex
from pathlib import Path

import slash.utils as utils


def hook(slash_exe: Path) -> str:
    """
    Generate a shell hook script.
    """
    s = utils.dals(
    """
    __slash_exe() (
        "%(slash_exe)s" "$@"
    )

    __slash_hashr() {
        if [ -n "${ZSH_VERSION:+x}" ]; then
            \\rehash
        elif [ -n "${POSH_VERSION:+x}" ]; then
            :  # pass
        else
            \\hash -r
        fi
    }

    __slash_activate() {
        \\local ask_slash
        ask_slash="$(PS1="${PS1:-}" __slash_exe shell "$@" --shell_pid "$$" )" || \\return
        \\eval "$ask_slash"
        __slash_hashr
    }

    __slash_deactivate() {
        \\local ask_slash
        ask_slash="$(PS1="${PS1:-}" __slash_exe shell "$@" --shell_pid "$$" )" || \\return
        \\eval "$ask_slash"
        __slash_hashr
    }

    slash() {
        \\local cmd="${1-__missing__}"
        case "$cmd" in
            activate)
                __slash_activate "$@"
                ;;
            deactivate)
                __slash_deactivate "$@"
                ;;
            *)
                __slash_exe "$@"
                ;;
        esac
    }
    """
    ) % {
        "slash_exe": slash_exe,
    }
    return s

def activate(env_name: str, port: int, stash: dict = None) -> str:
    """
    Generate a shell activation script.

    1. Set the http_proxy and https_proxy environment variables.
    2. Set the env stack variable.
    3. Setup proper PS1 for the shell.
    4. Remember previous proxy settings.
    """
    prompt_modifier = r"/{env_name}\ ".format(env_name=env_name)
    commands = [
        f'export http_proxy=http://127.0.0.1:{port}',
        f'export https_proxy=http://127.0.0.1:{port}',
        f'export SLASH_ENV={env_name}',
        f'export PS1="{prompt_modifier}$PS1"',
    ]

    if stash is not None:
        commands.append(f'export SLASH_STASH={shlex.quote(json.dumps(stash))}')

    return "\n".join(commands)

def deactivate() -> str:
    """
    Generate a shell deactivation script.

    1. Unset the http_proxy and https_proxy environment variables.
    2. Unset the env stack variable.
    3. Restore the PS1 for the shell.
    4. Restore previous proxy settings
    """
    ps1 = os.environ.get("PS1", "$")
    ps1 = re.sub(r"/\w+\\ ", "", ps1, count=1)
    commands = [
         'unset http_proxy',
         'unset https_proxy',
         'unset SLASH_ENV',
        f'export PS1="{ps1}"',
    ]

    stash = os.environ.get("SLASH_STASH", None)
    if stash is not None:
        stash = json.loads(stash)
        for key, value in stash.items():
            commands.append(f'export {key}={shlex.quote(value)}')
        commands.append('unset SLASH_STASH')

    return "\n".join(commands)
