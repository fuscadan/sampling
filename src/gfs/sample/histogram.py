import csv
import itertools
import os
from math import prod

from gfs.constants import DIRECTORY_PROJECT_ROOT
from gfs.sample.domain import Axis, Domain
from gfs.sample.tree import Tree


class Histogram(dict[tuple[int, ...], int]):
    def __init__(self, domain: Domain) -> None:
        self.domain = domain

        for grid_point in self._get_grid(domain):
            self[grid_point] = 0

    def _get_grid(self, domain: Domain) -> list[tuple[int, ...]]:
        axis_grid_points: list[tuple[int, ...]] = list()
        for axis in domain:
            axis_grid_points.append(tuple(range(1 << axis.bit_depth)))
        return list(itertools.product(*axis_grid_points))

    def _get_n_blocks(self) -> int:
        return sum(self.values())

    def populate(self, tree: Tree, n_samples: int) -> None:
        for i in range(0, n_samples):
            sample = tree.sample_once()
            projected_sample = tuple([sample[axis.id] for axis in self.domain])
            self[projected_sample] += 1

    @staticmethod
    def _get_scale(axis: Axis) -> float:
        a = axis.left_endpoint
        b = axis.right_endpoint
        return (b - a) / (1 << axis.bit_depth)

    def _rescale(self, coordinate: int, axis: Axis) -> float:
        a = axis.left_endpoint
        scale = self._get_scale(axis)
        return a + coordinate * scale

    def _to_list(
        self, normalize: bool, rescale: bool, density: bool
    ) -> list[list[float]]:
        vertical_scale: float = 1
        if normalize or density:
            n_blocks = self._get_n_blocks()
            vertical_scale = 1 / n_blocks
        if density:
            block_volume = prod([self._get_scale(axis) for axis in self.domain])
            vertical_scale = vertical_scale / block_volume

        hist_list: list[list[float]] = list()
        for int_coordinates, count in self.items():
            row: list[float] = list()
            for int_coordinate, axis in zip(int_coordinates, self.domain):
                coordinate = int_coordinate
                if rescale or density:
                    coordinate = self._rescale(coordinate, axis)
                row.append(coordinate)
            row.append(vertical_scale * count)
            hist_list.append(row)

        return hist_list

    def export(
        self,
        project: str,
        file: str,
        normalize: bool = True,
        rescale: bool = True,
        density: bool = False,
    ) -> None:
        hist_list = self._to_list(normalize, rescale, density)

        output_directory = os.path.join(DIRECTORY_PROJECT_ROOT, project, "output")
        os.makedirs(output_directory, exist_ok=True)
        file_path = os.path.join(output_directory, file)
        with open(file_path, "w") as f:
            writer = csv.writer(f)
            for row in hist_list:
                writer.writerow(row)
