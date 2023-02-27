import gc
from abc import ABC, abstractmethod
from typing import NamedTuple

from gfs.sample.algebra import multiply
from gfs.sample.functions import constant, linear
from gfs.sample.histogram import Histogram
from gfs.sample.leaf import LeafList
from gfs.sample.tree import Tree


class DataPoint(NamedTuple):
    id: int
    value: tuple[int]


class Posterior:
    def __init__(self, leaves: LeafList) -> None:
        self.leaves = leaves

    def histogram(self, n_samples: int) -> Histogram:
        tree = Tree(self.leaves)
        return tree.histogram(n_samples)


class Likelihood(ABC):
    def __init__(self, domain_bit_depth: int) -> None:
        self.domain_bit_depth = domain_bit_depth

    @abstractmethod
    def leaves(self, datum: DataPoint) -> LeafList:
        pass


class Prior(ABC):
    def __init__(self, domain_bit_depth: int) -> None:
        self.domain_bit_depth = domain_bit_depth
        self._leaves = self._get_initial_leaves()

    @property
    def leaves(self) -> LeafList:
        return self._leaves

    @leaves.setter
    def leaves(self, leaves: LeafList) -> None:
        del self._leaves
        gc.collect()
        self._leaves = leaves

    @abstractmethod
    def _get_initial_leaves(self) -> LeafList:
        pass

    def update(self, likelihood: Likelihood, data: list[DataPoint]) -> Posterior:
        for datum in data:
            print(f"Updating with datum: {datum}")
            self.leaves = multiply(likelihood.leaves(datum), self.leaves)

        return Posterior(self.leaves)


class BinomialLikelihood(Likelihood):
    def __init__(self, domain_bit_depth: int) -> None:
        super().__init__(domain_bit_depth)

    def leaves(self, datum: DataPoint) -> LeafList:
        if datum.value[0] == 0:
            return linear(domain_bit_depth=self.domain_bit_depth, reverse=False)
        if datum.value[0] == 1:
            return linear(domain_bit_depth=self.domain_bit_depth, reverse=True)

        raise ValueError(f"Invalid datum: {datum}")


class UniformPrior(Prior):
    def __init__(self, domain_bit_depth: int) -> None:
        super().__init__(domain_bit_depth=domain_bit_depth)

    def _get_initial_leaves(self) -> LeafList:
        return constant(domain_bit_depth=self.domain_bit_depth)
