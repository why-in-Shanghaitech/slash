import importlib
import tempfile
from pathlib import Path

import slash
import slash.core
from slash.core import constants


class TesterMixin:
    def setUp(self):
        self._temp_dir = tempfile.TemporaryDirectory()
        self._temp_dir_path = Path(self._temp_dir.name)
        constants.WORK_DIR = self._temp_dir_path
        constants.ENVS_DIR = self._temp_dir_path / "envs"
        constants.CONFIG_PATH = self._temp_dir_path / ".slashrc"

        importlib.reload(slash)
        importlib.reload(slash.core)
        importlib.reload(slash.core.envs)

    def tearDown(self):
        self._temp_dir.cleanup()
