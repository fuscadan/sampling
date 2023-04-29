import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass

from gfs.sample.algebra import multiply
from gfs.sample.domain import Domain
from gfs.sample.elements import (
    DataPoint,
    Distribution,
    Parameter,
    ParameterSamples,
    PredictiveDists,
    XDataPoint,
)
from gfs.sample.leaf import LeafList
from gfs.sample.tree import Tree

logger = logging.getLogger(__name__)


class Prior(LeafList):
    pass


class Posterior(LeafList):
    pass


class Likelihood(ABC):
    def __init__(self, domain: Domain) -> None:
        self.domain = domain

    @abstractmethod
    def leaves(self, datum: DataPoint) -> LeafList:
        pass


@dataclass
class Model(ABC):
    param_domain: Domain
    prior: Prior
    likelihood: Likelihood
    categories: tuple[str, ...]

    @abstractmethod
    def dist(self, param: Parameter, x: XDataPoint | None) -> Distribution:
        pass


def update_prior(
    prior: Prior,
    likelihood: Likelihood,
    data: list[DataPoint],
    leaf_bit_depth_range: int,
) -> Posterior:
    leaves = prior
    for datum in data:
        logger.info(f"Updating prior with datum: {datum}")
        leaves = multiply(likelihood.leaves(datum=datum), leaves, leaf_bit_depth_range)
        logger.debug(f"Number of leaves: {len(leaves)}")
    return Posterior(leaves)


def predict(
    model: Model, parameter_samples: ParameterSamples, x: XDataPoint | None
) -> PredictiveDists:
    predictions = PredictiveDists()
    logger.info(f"Predicting: model={model.__class__.__name__}, x={x}")
    for parameter in parameter_samples:
        predictions.append(model.dist(parameter, x))
    logger.info(f"Average predictive distribution: {predictions.mean}")
    return predictions


def sample(
    posterior: Posterior, domain: Domain, n_posterior_samples: int
) -> ParameterSamples:
    logger.info(f"Sampling posterior: n_posterior_samples={n_posterior_samples}")
    samples = ParameterSamples()
    tree = Tree(leaves=posterior)
    logger.debug(f"Sampling posterior: tree.depth={tree.depth}")
    logger.debug(f"Sampling posterior: tree.n_blocks={tree.n_blocks}")
    for i in range(n_posterior_samples):
        samples.append(Parameter(domain.scale(tree.sample_once())))
    return samples
