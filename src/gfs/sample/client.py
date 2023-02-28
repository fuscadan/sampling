from typing import Any

import click

from gfs.sample.bayes import BinomialLikelihood, Likelihood, Prior, UniformPrior
from gfs.sample.infer import infer_parameters
from gfs.sample.utils import load_config

REQUIRED_KWARGS_CLI_INFER = [
    "project",
    "likelihood",
    "prior",
    "domain_bit_depth",
    "bit_depth_range",
    "n_data_points",
    "n_samples",
    "data_file",
]

REQUIRED_KWARGS_INFER = [
    "project",
    "likelihood",
    "prior",
    "n_data_points",
    "n_samples",
    "data_file",
    "output_file",
]

LIKELIHOODS: dict[str, type[Likelihood]] = {
    "binomial": BinomialLikelihood,
}

PRIORS: dict[str, type[Prior]] = {
    "uniform": UniformPrior,
}


def _default_output_file(kwargs: dict[str, Any]) -> str:
    project: str = kwargs["project"]
    n_data_points: int = kwargs["n_data_points"]
    n_samples: int = kwargs["n_samples"]

    prefix = f"{project.replace('_','-')}_"
    if kwargs.get("tag") is not None:
        tag: str = kwargs["tag"]
        prefix = prefix + f"{tag.replace('_','-')}_"

    suffix = f"n-data-points-{n_data_points}_n-samples-{n_samples}.csv"

    return prefix + suffix


def _process_kwargs_infer(kwargs: dict[str, Any]) -> dict[str, Any]:
    project: str = kwargs["project"]

    # pull kwargs from config file, then update with any kwargs from command line
    processed: dict[str, Any] = dict()
    if kwargs.get("config") is not None:
        processed.update(load_config(project=project, file=kwargs["config"]))
    for k, v in kwargs.items():
        if v is not None:
            processed[k] = v

    # check required kwargs are present
    for key in REQUIRED_KWARGS_CLI_INFER:
        if processed.get(key) is None:
            raise ValueError(
                f"Missing keyword argument '{key}'. Either set a value for '{key}' "
                f"in the config file or pass it as a command line argument with "
                f"'--{key}=<value>'."
            )

    # build Likelihood and Prior objects
    domain_bit_depth = processed["domain_bit_depth"]
    bit_depth_range = processed["bit_depth_range"]
    likelihood = LIKELIHOODS[processed["likelihood"]](domain_bit_depth)
    prior = PRIORS[processed["prior"]](domain_bit_depth, bit_depth_range)
    processed["likelihood"] = likelihood
    processed["prior"] = prior

    # handle default output file
    if processed.get("output_file") is None:
        processed["output_file"] = _default_output_file(processed)

    # only keep kwargs required for infer_parameters
    processed = {k: v for k, v in processed.items() if k in REQUIRED_KWARGS_INFER}

    return processed


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--project", type=str, required=True)
@click.option("--config", type=str)
@click.option("--tag", type=str)
@click.option("--likelihood", type=str)
@click.option("--prior", type=str)
@click.option("--domain_bit_depth", type=int)
@click.option("--n_data_points", type=int)
@click.option("--n_samples", type=int)
@click.option("--data_file", type=str)
@click.option("--output_file", type=str)
def infer(**kwargs) -> None:
    processed = _process_kwargs_infer(kwargs)
    infer_parameters(**processed)
