import os

import yaml

from gfs.constants import DIRECTORY_CONFIGS


def mock_infer(config: str) -> None:
    """placeholder for the main function called by the client"""
    file_path = os.path.join(DIRECTORY_CONFIGS, f"{config}.yaml")
    with open(file_path) as f:
        config_dict = yaml.safe_load(f)

    print(config_dict)
