import gc
import logging
from abc import ABC, abstractmethod
from typing import NamedTuple

from gfs.sample.algebra import multiply
from gfs.sample.domain import Domain
from gfs.sample.functions import constant, linear
from gfs.sample.histogram import Histogram
from gfs.sample.leaf import LeafList
from gfs.sample.tree import Tree

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataPoint(NamedTuple):
    id: int
    value: tuple[int]


class Posterior:
    def __init__(self, leaves: LeafList, domain: Domain) -> None:
        self.leaves = leaves
        self.domain = domain

    def histogram(self, n_samples: int, axes: list[int]) -> Histogram:
        tree = Tree(self.leaves)
        logger.debug(f"Tree depth: {tree.depth}")
        subdomain = Domain([axis for axis in self.domain if axis.id in axes])
        histogram = Histogram(domain=subdomain)
        histogram.populate(tree=tree, n_samples=n_samples)
        return histogram


class Likelihood(ABC):
    def __init__(self, domain: Domain) -> None:
        self.domain = domain

    @abstractmethod
    def leaves(self, datum: DataPoint) -> LeafList:
        pass


class Prior(ABC):
    def __init__(self, domain: Domain, leaf_bit_depth_range: int) -> None:
        self.domain = domain
        self.leaf_bit_depth_range = leaf_bit_depth_range
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
            logger.info(f"Updating prior with datum: {datum}")
            self.leaves = multiply(likelihood.leaves(datum), self.leaves)
            self.leaves.combine_on_multiplicity()
            max_bit_depth = max([leaf.bit_depth for leaf in self.leaves])
            self.leaves.drop_small(bit_depth=max_bit_depth - self.leaf_bit_depth_range)
            self.leaves.reduce_multiplicity()
            logger.debug(f"Length of leaves: {len(self.leaves)}")

        return Posterior(leaves=self.leaves, domain=self.domain)


class BinomialLikelihood(Likelihood):
    def __init__(self, domain: Domain) -> None:
        super().__init__(domain)
        if len(domain) != 1:
            raise ValueError("BinomialLikelihood only defined on 1D domains.")
        self.domain_bit_depth = domain[0].bit_depth

    def leaves(self, datum: DataPoint) -> LeafList:
        if datum.value[0] == 0:
            return linear(domain_bit_depth=self.domain_bit_depth, reverse=False)
        if datum.value[0] == 1:
            return linear(domain_bit_depth=self.domain_bit_depth, reverse=True)

        raise ValueError(f"Invalid datum: {datum}")


class UniformPrior(Prior):
    def __init__(self, domain: Domain, leaf_bit_depth_range: int) -> None:
        super().__init__(domain=domain, leaf_bit_depth_range=leaf_bit_depth_range)

    def _get_initial_leaves(self) -> LeafList:
        return constant(domain_bit_depths=[axis.bit_depth for axis in self.domain])
