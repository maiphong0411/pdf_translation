import os

import yaml
from dotenv import load_dotenv

from .log_utils import get_logger

SOURCE_DIR = os.path.join(os.path.dirname(__file__), "..")
CONFIG_DIR = os.path.join(SOURCE_DIR, "configs")
ENV_PATH = os.path.join(CONFIG_DIR, ".env")
if not os.path.exists(ENV_PATH):
    raise FileNotFoundError(f"Environment file not found at {ENV_PATH}")
load_dotenv(ENV_PATH)

ENV = os.environ.get("ENV", "dev")  # default to dev
CONFIG_PATH = os.path.join(CONFIG_DIR, f"config.{ENV}.yml")

if not os.path.exists(CONFIG_PATH):
    raise FileNotFoundError(f"Config file not found at {CONFIG_PATH}")

with open(CONFIG_PATH, "r") as f:
    configs = yaml.safe_load(f)
logger = get_logger(__file__)


def get_env(env_name: str, default=None):
    if env_name not in os.environ:
        logger.warning(f"Environment variable {env_name} not found")
    value = os.environ.get(env_name, default=default)
    return value


def get_config(key: str, sub_key: str = None, default=None):
    if key not in configs:
        logger.warning(f"Key {key} not found in config")
        return default
    if sub_key:
        if sub_key not in configs[key]:
            logger.warning(f"Subkey {key}/{sub_key} not found in config")
            return default
        value = configs[key][sub_key]
    else:
        value = configs[key]
    # Check if value start with os.environ, then replace it with the value
    if isinstance(value, str) and value.startswith("os.environ/"):
        value = get_env(value.split("/")[1], default=default)
    return value
