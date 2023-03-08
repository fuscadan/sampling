from typing import Any

import click

from gfs.sample.bayes import BinomialLikelihood, Likelihood, Prior, UniformPrior
from gfs.sample.domain import Axis, Domain
from gfs.sample.infer import infer_parameters
from gfs.sample.utils import load_config

LIKELIHOODS: dict[str, type[Likelihood]] = {
    "binomial": BinomialLikelihood,
}

PRIORS: dict[str, type[Prior]] = {
    "uniform": UniformPrior,
}


def _default_output_file(
    project: str, n_data_points: int, n_samples: int, tag: str | None = None
) -> str:
    prefix = f"{project.replace('_','-')}_"
    if tag is not None:
        prefix = prefix + f"{tag.replace('_','-')}_"
    suffix = f"n-data-points-{n_data_points}_n-samples-{n_samples}.csv"

    return prefix + suffix


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--project", type=str, required=True)
@click.option("--config", type=str, required=True)
def infer(project: str, config: str) -> None:
    config_dict = load_config(project=project, file=config)

    tag = config_dict.get("tag")
    n_data_points = config_dict["likelihood"]["n_data_points"]
    n_samples = config_dict["histogram"]["n_samples"]
    domain = Domain(
        [Axis(**axis_kwargs) for axis_kwargs in config_dict["prior"]["domain"]]
    )
    leaf_bit_depth_range = config_dict["performance"]["leaf_bit_depth_range"]
    likelihood = LIKELIHOODS[config_dict["likelihood"]["name"]](domain)
    prior = PRIORS[config_dict["prior"]["name"]](domain, leaf_bit_depth_range)

    output_file = config_dict["io"].get("output_file")
    if output_file is None:
        output_file = _default_output_file(project, n_data_points, n_samples, tag)

    infer_kwargs: dict[str, Any] = {
        "project": project,
        "prior": prior,
        "likelihood": likelihood,
        "n_data_points": n_data_points,
        "n_samples": config_dict["histogram"]["n_samples"],
        "data_file": config_dict["io"]["data_file"],
        "output_file": output_file,
        "histogram_axes": config_dict["histogram"]["axes"],
    }
    infer_parameters(**infer_kwargs)
