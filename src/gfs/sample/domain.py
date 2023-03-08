from typing import NamedTuple


class Axis(NamedTuple):
    id: int
    left_endpoint: float
    right_endpoint: float
    bit_depth: int


class Domain(list[Axis]):
    pass
