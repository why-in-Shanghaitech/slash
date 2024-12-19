import re
from pathlib import Path

import slash.utils as utils


logger = utils.logger


def initialize(slash_exe: Path) -> bool:
    """
    Initialize slash for the current user in the shell.

    Arguments:
        slash_exe: The path to the slash executable.

    Returns:
        is_modified: Whether the shell configuration file was modified.
    """
    SLASH_INITIALIZE_RE_BLOCK = (
        r"^# >>> slash initialize >>>(?:\n|\r\n)"
        r"([\s\S]*?)"
        r"# <<< slash initialize <<<(?:\n|\r\n)?"
    )

    user_rc_path = Path.home() / ".bashrc"

    try:
        with open(user_rc_path) as fh:
            rc_content = fh.read()
    except FileNotFoundError:
        rc_content = ""
    except:
        raise

    rc_original_content = rc_content

    slash_initialize_content = utils.dals(
    """
    # >>> slash initialize >>>
    # !! Contents within this block are managed by 'slash init' !!
    __slash_setup="$('%(slash_exe)s' 'shell' 'hook' 2> /dev/null)"
    if [ $? -eq 0 ]; then
        eval "$__slash_setup"
    fi
    unset __slash_setup
    # <<< slash initialize <<<
    """
    ) % {
        "slash_exe": slash_exe,
    }

    replace_str = "__SLASH_REPLACE_ME_B612__"

    rc_search = re.search(
        SLASH_INITIALIZE_RE_BLOCK,
        rc_content,
        flags=re.MULTILINE,
    )
    if rc_search:
        rc_content = re.sub(
            SLASH_INITIALIZE_RE_BLOCK,
            replace_str,
            rc_content,
            flags=re.MULTILINE,
        )
        # it is only possible to have one block of slash initialize captured
        # if there is more than one, we will replace all the content between the first and last block
        rc_content = rc_content.replace(replace_str, slash_initialize_content)
    else:
        rc_content += f"\n{slash_initialize_content}\n"

    with open(user_rc_path, "w") as fh:
        fh.write(rc_content)

    is_modified = rc_content != rc_original_content

    if is_modified:
        logger.info("{:<14}{}".format("modified", user_rc_path))
        logger.info("==> For changes to take effect, close and re-open your current shell. <==")
    else:
        logger.info("{:<14}{}".format("no change", user_rc_path))
        logger.info("No action taken.")

    return is_modified
