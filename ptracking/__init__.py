import os
import yaml
from pathlib import Path

__all__ = ["ROOT_DIR" "config"]
ROOT_DIR = Path(__file__).absolute().parent.parent


def _load_yml(filename) -> dict:
    with open(ROOT_DIR.joinpath(filename), "r") as fp:
        return yaml.safe_load(fp)


config = _load_yml("config.yml")

# if a dev config exists, merge the root-level entries only
# non-recursively
if os.path.exists(ROOT_DIR.joinpath("config.dev.yml")):
    dev_config = _load_yml("config.dev.yml")
    for key, val in dev_config.items():
        config[key] = {**config[key], **val}
