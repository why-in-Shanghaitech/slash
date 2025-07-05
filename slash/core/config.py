from dataclasses import dataclass, field
from typing import Any, Optional

from filelock import SoftFileLock
from ruamel.yaml import YAML

import slash.utils as utils
from slash.core.constants import CONFIG_PATH


logger = utils.logger
yaml = YAML()

@dataclass
class SlashConfig:
    http_server: Optional[str] = field(
        default=None,
        metadata={
            "help": "Route all HTTP requests to the specified server."
        }
    )
    http_port: Optional[int] = field(
        default=None,
        metadata={
            "help": "Route all HTTP requests to the specified port.",
            "serializer": lambda x: int(x)
        }
    )

class ConfigManager:
    def __init__(self):
        self._lock = SoftFileLock(CONFIG_PATH.with_suffix(".lock"))
        if not CONFIG_PATH.exists():
            logger.debug(f"Creating a new configuration file at {CONFIG_PATH}")
            CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
            self.save({})

    def load(self) -> dict:
        with open(CONFIG_PATH, "r") as f:
            content = yaml.load(f)

        return content

    def save(self, config: dict) -> None:
        with open(CONFIG_PATH, "w") as f:
            yaml.dump(config, f)

    def get_config(self) -> SlashConfig:
        with self._lock:
            return SlashConfig(**self.load())


    # for each operation, we need to acquire the lock
    def show(self) -> None:
        with self._lock:
            with open(CONFIG_PATH, "r") as f:
                print(f.read())

    def get(self, key: str) -> Any:
        if key not in SlashConfig.__dataclass_fields__:
            raise KeyError(f"'{key}' is not a Slash config key.")

        with self._lock:
            config = self.load()
            return config.get(key, None)

    def set(self, key: str, value: Any) -> None:
        if key not in SlashConfig.__dataclass_fields__:
            raise KeyError(f"'{key}' is not a Slash config key.")

        if isinstance(value, str):
            serializer = SlashConfig.__dataclass_fields__[key].metadata.get("serializer", lambda x: x)
            value = serializer(value)

        with self._lock:
            config = self.load()
            config[key] = value
            self.save(config)

    def remove_key(self, key: str) -> None:
        with self._lock:
            config = self.load()
            if key in config:
                del config[key]
            self.save(config)
