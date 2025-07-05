"""Constants used throughout the Slash codebase"""
from pathlib import Path


WORK_DIR = Path.home() / ".cache" / "slash"
ENVS_DIR = WORK_DIR / "envs"
CONFIG_PATH = WORK_DIR / ".slashrc"
