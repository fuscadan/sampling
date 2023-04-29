from abc import ABC, abstractmethod
from dataclasses import dataclass

from gfs.app.bayes import Model
from gfs.app.elements import DataPoint
from gfs.constants import LEAF_BIT_DEPTH_RANGE


class Preprocessor(ABC):
    def __repr__(self) -> str:
        return self.__class__.__name__

    @abstractmethod
    def process_row(self, row: list[str]) -> DataPoint:
        pass


@dataclass
class ProjectIO:
    training_data_file: str
    input_data_file: str
    preprocessor: Preprocessor
    prior_file: str | None
    posterior_file: str
    posterior_samples_file: str
    prediction_file: str


@dataclass
class ProjectParams:
    n_posterior_samples: int
    n_data_points: int
    leaf_bit_depth_range: int = LEAF_BIT_DEPTH_RANGE


@dataclass
class Project:
    name: str
    tags: list[str]
    model: Model
    io: ProjectIO
    params: ProjectParams

    @property
    def _template_values(self) -> dict[str, str]:
        return {
            "project_name": self.name,
            "tags": "_".join(self.tags),
            "n_posterior_samples": str(self.params.n_posterior_samples),
            "n_data_points": str(self.params.n_data_points),
        }

    def _render(self, input: str) -> str:
        output = input
        for k, v in self._template_values.items():
            output = output.replace(f"<< {k} >>", v)
        return output

    @property
    def training_data_file(self) -> str:
        return self._render(self.io.training_data_file)

    @property
    def input_data_file(self) -> str:
        return self._render(self.io.input_data_file)

    @property
    def prior_file(self) -> str | None:
        if self.io.prior_file is not None:
            return self._render(self.io.prior_file)

    @property
    def posterior_file(self) -> str:
        return self._render(self.io.posterior_file)

    @property
    def posterior_samples_file(self) -> str:
        return self._render(self.io.posterior_samples_file)

    @property
    def prediction_file(self) -> str:
        return self._render(self.io.prediction_file)
