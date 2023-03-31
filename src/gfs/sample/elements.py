import logging
from typing import Iterable, NamedTuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPoint(NamedTuple):
    id: int
    value: tuple[int, ...]


class Parameter(tuple[float, ...]):
    def __init__(self, iterable: Iterable):
        if len(self) == 0:
            raise ValueError("Parameter cannot be empty.")


class Distribution(tuple[float, ...]):
    def __init__(self, iterable: Iterable):
        if round(sum(self), 6) != 1:
            raise ValueError("Distribution must sum to 1.")


class Histogram(dict[Parameter, int]):
    def __missing__(self, key):
        return 0


class PosteriorSamples(list[Parameter]):
    def __init__(self, iterable: Iterable, axes: list[str]) -> None:
        list.__init__(self, iterable)
        self.axes = axes

    @property
    def histogram(self) -> Histogram:
        hist = Histogram()
        for sample in self:
            hist[sample] += 1
        return hist


class PredictiveDists(list[Distribution]):
    def __init__(self, iterable: Iterable, categories: list[str]) -> None:
        list.__init__(self, iterable)
        self.categories = categories

    @property
    def mean(self) -> Distribution:
        cat_means: list[float] = list()
        n_dists = len(self)
        for i in range(len(self.categories)):
            cat_means.append(sum([dist[i] for dist in self]) / n_dists)

        return Distribution(cat_means)
