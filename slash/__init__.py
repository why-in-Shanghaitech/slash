from .slash import Slash
from .cli import main

import logging

logger = logging.getLogger("slash")

# Set up logging
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    # handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
