import logging
from typing import Iterable, NamedTuple

logger = logging.getLogger(__name__)


class XDataPoint(tuple[float, ...]):
    pass


class YDataPoint(tuple[float, ...]):
    pass


class DataPoint(NamedTuple):
    id: int
    x: XDataPoint | None = None
    y: YDataPoint | None = None


class Parameter(tuple[float, ...]):
    def __init__(self, iterable: Iterable[float]):
        if len(self) == 0:
            raise ValueError("Parameter cannot be empty.")


class Histogram(dict[Parameter, int]):
    def __missing__(self, key):
        return 0


class ParameterSamples(list[Parameter]):
    @property
    def histogram(self) -> Histogram:
        hist = Histogram()
        for sample in self:
            hist[sample] += 1
        return hist


class Distribution(tuple[float, ...]):
    def __init__(self, iterable: Iterable[float]):
        if round(sum(self), 6) != 1:
            raise ValueError("Distribution must sum to 1.")


class PredictiveDists(list[Distribution]):
    @property
    def mean(self) -> Distribution:
        n_dists = len(self)
        if n_dists == 0:
            raise ValueError("Cannot compute mean distribution of empty list.")

        category_means: list[float] = list()
        n_categories = len(self[0])
        for i in range(n_categories):
            category_means.append(sum([dist[i] for dist in self]) / n_dists)

        return Distribution(category_means)
