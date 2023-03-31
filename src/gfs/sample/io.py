import csv
import logging
import os
from abc import ABC, abstractmethod

from gfs.sample.elements import DataPoint, PosteriorSamples, PredictiveDists, Sample

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Preprocessor(ABC):
    @abstractmethod
    def process_row(self, row: list[str]) -> DataPoint:
        pass


class ProjectIO:
    def __init__(
        self,
        data_file: str,
        preprocessor: Preprocessor,
        posterior_file: str,
        prediction_file: str,
    ) -> None:
        self.data_file = data_file
        self.preprocessor = preprocessor
        self.posterior_file = posterior_file
        self.prediction_file = prediction_file

    def __repr__(self) -> str:
        msg = (
            "ProjectIO("
            f"data_file='{self.data_file}', "
            f"preprocessor='{self.preprocessor}', "
            f"posterior_file='{self.posterior_file}', "
            f"prediction_file='{self.prediction_file}')"
        )
        return msg

    @staticmethod
    def _render(input: str, template_values: dict[str, str]) -> str:
        output = input
        for k, v in template_values.items():
            output = output.replace(f"<< {k} >>", v)
        return output

    def load_data(self) -> list[DataPoint]:
        with open(self.data_file) as f:
            reader = csv.reader(f)
            data = [self.preprocessor.process_row(row) for row in reader]
        logger.info(f"Loaded data: {self.data_file}")
        return data

    def load_posterior(self, template_values: dict[str, str]) -> PosteriorSamples:
        posterior_file = self._render(
            input=self.posterior_file, template_values=template_values
        )
        with open(posterior_file) as f:
            reader = csv.reader(f)
            axes = next(reader)
            samples = PosteriorSamples(
                [Sample([float(item) for item in row]) for row in reader], axes=axes
            )
        logger.info(f"Loaded posterior samples: {posterior_file}")
        return samples

    def _export(
        self, filepath: str, data: list[list[float]], header: list[str]
    ) -> None:
        filepath_tokens = filepath.split("/")
        directory = "/".join(filepath_tokens[:-1])
        file = filepath_tokens[-1]

        os.makedirs(directory, exist_ok=True)
        filepath = os.path.join(directory, file)
        with open(filepath, "w") as f:
            writer = csv.writer(f)
            writer.writerow(header)
            for row in data:
                writer.writerow(row)
        logger.info(f"Exported file: {filepath}")

    def export_posterior(
        self, posterior_samples: PosteriorSamples, template_values: dict[str, str]
    ) -> None:
        posterior_file = self._render(
            input=self.posterior_file, template_values=template_values
        )
        self._export(
            filepath=posterior_file,
            data=[list(sample) for sample in posterior_samples],
            header=posterior_samples.axes,
        )

    def export_posterior_histogram(
        self, posterior_samples: PosteriorSamples, template_values: dict[str, str]
    ) -> None:
        posterior_histogram_file = self._render(
            input=self.posterior_file.replace(".csv", "_histogram.csv"),
            template_values=template_values,
        )
        hist = posterior_samples.histogram
        self._export(
            filepath=posterior_histogram_file,
            data=[list(sample) + [value] for sample, value in hist.items()],
            header=posterior_samples.axes + ["count"],
        )

    def export_prediction(
        self, predictive_dists: PredictiveDists, template_values: dict[str, str]
    ) -> None:
        prediction_file = self._render(
            input=self.prediction_file, template_values=template_values
        )
        self._export(
            filepath=prediction_file,
            data=[list(predictive_dists.mean)],
            header=predictive_dists.categories,
        )


class BinomialPreprocessor(Preprocessor):
    def process_row(self, row: list[str]) -> DataPoint:
        return DataPoint(id=int(row[0]), value=(int(row[1]),))
