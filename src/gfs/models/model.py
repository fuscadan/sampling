from abc import ABC, abstractmethod
from dataclasses import dataclass

from gfs.sample.bayes import Likelihood, Prior
from gfs.sample.domain import Domain
from gfs.sample.elements import Distribution, Parameter, XDataPoint


@dataclass
class Model(ABC):
    param_domain: Domain
    prior: Prior
    likelihood: Likelihood
    categories: tuple[str, ...]

    @abstractmethod
    def dist(self, param: Parameter, x: XDataPoint | None) -> Distribution:
        pass
