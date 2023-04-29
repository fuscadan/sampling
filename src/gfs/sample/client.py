import argparse
import logging
import os

from gfs.constants import VERSION, get_logging_level
from gfs.sample.bayes import Likelihood, Posterior, Prior, predict, sample, update_prior
from gfs.sample.elements import DataPoint
from gfs.sample.io import (
    export_histogram,
    export_leaves,
    export_prediction,
    export_samples,
    load_data,
    load_leaves,
    load_project,
    load_samples,
)
from gfs.sample.project import Project

logger = logging.getLogger(__name__)


def cli_update_prior(project: Project) -> None:
    data: list[DataPoint] = load_data(
        data_file=project.training_data_file, preprocessor=project.io.preprocessor
    )
    if project.prior_file is not None:
        prior: Prior = Prior(load_leaves(project.prior_file))
    else:
        prior: Prior = project.model.prior
    likelihood: Likelihood = project.model.likelihood
    posterior = update_prior(
        prior=prior,
        likelihood=likelihood,
        data=data[: project.params.n_data_points],
        leaf_bit_depth_range=project.params.leaf_bit_depth_range,
    )
    export_leaves(leaves=posterior, filepath=project.posterior_file)


def cli_sample_posterior(project: Project) -> None:
    samples = sample(
        posterior=Posterior(load_leaves(filepath=project.posterior_file)),
        domain=project.model.param_domain,
        n_posterior_samples=project.params.n_posterior_samples,
    )
    export_samples(
        samples=samples,
        filepath=project.posterior_samples_file,
        domain=project.model.param_domain,
    )


def cli_histogram(project: Project) -> None:
    samples = load_samples(filepath=project.posterior_samples_file)
    output_path = project.posterior_samples_file.replace(".csv", "__histogram.csv")
    export_histogram(
        samples=samples, filepath=output_path, domain=project.model.param_domain
    )


def cli_predict(project: Project) -> None:
    input_data: list[DataPoint] = load_data(
        data_file=project.input_data_file, preprocessor=project.io.preprocessor
    )
    parameter_samples = load_samples(filepath=project.posterior_samples_file)
    for datum in input_data:
        output_path = project.prediction_file.replace(".csv", f"__id-{datum.id}.csv")
        predictions = predict(
            model=project.model, parameter_samples=parameter_samples, x=datum.x
        )
        export_prediction(
            predictions=predictions,
            filepath=output_path,
            categories=project.model.categories,
        )


parser = argparse.ArgumentParser()
parser.add_argument("--version", action="version", version=VERSION)
parser.add_argument("--debug", action="store_true")
parser.add_argument("--config")

subparsers = parser.add_subparsers(required=True)

update_prior_parser = subparsers.add_parser("update_prior")
update_prior_parser.add_argument("--tags", nargs="*")
update_prior_parser.add_argument("--prior_file")
update_prior_parser.add_argument("--posterior_file")
update_prior_parser.add_argument("--data_file")
update_prior_parser.add_argument("--n_data_points", type=int)
update_prior_parser.set_defaults(func=cli_update_prior)

sample_posterior_parser = subparsers.add_parser("sample_posterior")
sample_posterior_parser.add_argument("--tags", nargs="*")
sample_posterior_parser.add_argument("--posterior_file")
sample_posterior_parser.add_argument("--posterior_samples_file")
sample_posterior_parser.add_argument("--n_posterior_samples", type=int)
sample_posterior_parser.set_defaults(func=cli_sample_posterior)

histogram_parser = subparsers.add_parser("histogram")
histogram_parser.add_argument("--tags", nargs="*")
histogram_parser.add_argument("--posterior_samples_file")
histogram_parser.set_defaults(func=cli_histogram)

predict_parser = subparsers.add_parser("predict")
predict_parser.add_argument("--tags", nargs="*")
predict_parser.add_argument("--input_data_file")
predict_parser.add_argument("--posterior_samples_file")
predict_parser.set_defaults(func=cli_predict)


def cli():
    kwargs = vars(parser.parse_args())

    if kwargs.get("debug"):
        os.environ["LOGGING"] = "DEBUG"
    logging.basicConfig(level=get_logging_level())

    project = load_project(**kwargs)
    kwargs["func"](project=project)
