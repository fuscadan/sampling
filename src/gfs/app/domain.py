from typing import NamedTuple


class Axis(NamedTuple):
    name: str
    left_endpoint: float
    right_endpoint: float
    bit_depth: int


class Domain(list[Axis]):
    @property
    def bit_depth(self):
        return sum([axis.bit_depth for axis in self])

    @staticmethod
    def _get_scale(axis: Axis) -> float:
        a = axis.left_endpoint
        b = axis.right_endpoint
        return (b - a) / (1 << axis.bit_depth)

    def _rescale(self, axis: Axis, coordinate: int) -> float:
        a = axis.left_endpoint
        scale = self._get_scale(axis)
        return a + coordinate * scale

    def scale(self, int_coords: tuple[int, ...]) -> tuple[float, ...]:
        if len(self) != len(int_coords):
            raise ValueError(
                "Number of integer coordinates not equal to dimension of Domain."
            )

        float_coords = [
            self._rescale(axis, coordinate)
            for axis, coordinate in zip(self, int_coords)
        ]

        return tuple(float_coords)
