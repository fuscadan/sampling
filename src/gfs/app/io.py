import csv
import json
import logging
import os
import tomllib
from typing import Any, Type

from gfs.app.bayes import Model
from gfs.app.domain import Domain
from gfs.app.elements import DataPoint, Parameter, ParameterSamples, PredictiveDists
from gfs.app.project import Preprocessor, Project, ProjectIO, ProjectParams
from gfs.constants import LEAF_BIT_DEPTH_RANGE
from gfs.models.binomial import BinomialModel, BinomialPreprocessor
from gfs.sample.leaf import Leaf, LeafList, Side

logger = logging.getLogger(__name__)


MODELS: dict[str, Type[Model]] = {
    "binomial": BinomialModel,
}
PREPROCESSORS: dict[str, Type[Preprocessor]] = {
    "binomial": BinomialPreprocessor,
}


class LeafDecoder(json.JSONDecoder):
    def decode(self, s: str) -> LeafList:
        raw_leaves = super().decode(s)
        leaves: LeafList = LeafList()
        for raw_leaf in raw_leaves:
            leaves.append(
                Leaf(
                    multiplicity=raw_leaf[0],
                    sides=[
                        Side(endpoint=raw_side[0], bit_depth=raw_side[1])
                        for raw_side in raw_leaf[1]
                    ],
                )
            )
        return leaves


def _make_dir(filepath: str) -> None:
    filepath_tokens = filepath.split("/")
    directory = "/".join(filepath_tokens[:-1])
    os.makedirs(directory, exist_ok=True)


def load_data(data_file: str, preprocessor: Preprocessor) -> list[DataPoint]:
    with open(data_file, "r") as f:
        reader = csv.reader(f)
        data = [preprocessor.process_row(row) for row in reader]
    logger.info(f"Loaded data: {data_file}")
    return data


def load_leaves(filepath: str) -> LeafList:
    with open(filepath, "r") as f:
        leaves: LeafList = json.load(f, cls=LeafDecoder)
    logger.info(f"Loaded leaves: {filepath}")
    return leaves


def export_leaves(leaves: LeafList, filepath: str) -> None:
    _make_dir(filepath=filepath)
    with open(filepath, "w") as f:
        json.dump(leaves, f)
    logger.info(f"Exported leaves: {filepath}")


def load_samples(filepath: str, header: bool = True) -> ParameterSamples:
    samples = ParameterSamples()
    with open(filepath) as f:
        reader = csv.reader(f)
        if header:
            _ = next(reader)
        for row in reader:
            float_row = [float(v) for v in row]
            samples.append(Parameter(float_row))
    logger.info(f"Loaded samples: {filepath}")
    return samples


def export_samples(samples: ParameterSamples, filepath: str, domain: Domain) -> None:
    _make_dir(filepath=filepath)
    with open(filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow([axis.name for axis in domain])
        for sample in samples:
            writer.writerow(sample)
    logger.info(f"Exported samples: {filepath}")


def export_histogram(samples: ParameterSamples, filepath: str, domain: Domain) -> None:
    hist = samples.histogram
    _make_dir(filepath=filepath)
    with open(filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow([axis.name for axis in domain] + ["count"])
        for parameter, count in hist.items():
            writer.writerow(list(parameter) + [count])
    logger.info(f"Exported histogram: {filepath}")


def export_prediction(
    predictions: PredictiveDists, filepath: str, categories: tuple[str]
) -> None:
    _make_dir(filepath=filepath)
    with open(filepath, "w") as f:
        writer = csv.writer(f)
        writer.writerow(categories)
        writer.writerow(predictions.mean)
    logger.info(f"Exported prediction: {filepath}")


def load_project(**kwargs) -> Project:
    config_file = kwargs["config"]
    with open(config_file, "rb") as f:
        config = tomllib.load(f)

    config_model: dict[str, Any] = config["model"]
    config_params: dict[str, Any] = config["params"]
    config_io: dict[str, Any] = config["io"]
    config_preprocessor: dict[str, Any] = config_io["preprocessor"]

    model_name: str = config_model["name"]
    model_kwargs: dict[str, Any] = config_model["kwargs"]
    preprocessor_name: str = config_preprocessor["name"]
    preprocessor_kwargs: dict[str, Any] = config_preprocessor["kwargs"]

    project_io = ProjectIO(
        training_data_file=(
            kwargs.get("training_data_file") or config_io["training_data_file"]
        ),
        input_data_file=(kwargs.get("input_data_file") or config_io["input_data_file"]),
        preprocessor=PREPROCESSORS[preprocessor_name](**preprocessor_kwargs),
        prior_file=(kwargs.get("prior_file") or config_io.get("prior_file")),
        posterior_file=kwargs.get("posterior_file") or config_io["posterior_file"],
        posterior_samples_file=(
            kwargs.get("posterior_samples_file") or config_io["posterior_samples_file"]
        ),
        prediction_file=(kwargs.get("prediction_file") or config_io["prediction_file"]),
    )

    params = ProjectParams(
        n_posterior_samples=(
            kwargs.get("n_posterior_samples") or config_params["n_posterior_samples"]
        ),
        n_data_points=kwargs.get("n_data_points") or config_params["n_data_points"],
        leaf_bit_depth_range=(
            config_params.get("leaf_bit_depth_range") or LEAF_BIT_DEPTH_RANGE
        ),
    )

    project = Project(
        name=kwargs.get("name") or config["name"],
        tags=kwargs.get("tags") or config.get("tags") or [],
        model=MODELS[model_name](**model_kwargs),
        io=project_io,
        params=params,
    )

    return project
