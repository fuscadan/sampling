import csv
import os

import yaml

from gfs.constants import DIRECTORY_PROJECT_ROOT
from gfs.sample.bayes import DataPoint


def randint(n_bits) -> int:
    """
    slower but possibly better random number generation compared to random.randrange
    """
    n_bytes = (n_bits // 8) + ((n_bits % 8) + 7) // 8
    return int.from_bytes(os.urandom(n_bytes)) >> (8 * n_bytes - n_bits)


def load_config(project: str, file: str) -> dict:
    file_path = os.path.join(DIRECTORY_PROJECT_ROOT, project, "configuration", file)
    with open(file_path) as f:
        config_dict = yaml.safe_load(f)
    return config_dict


def load_data(project: str, file: str) -> list[DataPoint]:
    file_path = os.path.join(DIRECTORY_PROJECT_ROOT, project, "data", file)
    with open(file_path) as f:
        reader = csv.reader(f)
        data: list[DataPoint] = list()
        for row in reader:
            int_row = list(map(int, row))
            id = int_row[0]
            value = tuple(int_row[1:])
            data.append(DataPoint(id=id, value=value))
    return data
