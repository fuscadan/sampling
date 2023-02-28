import logging

from gfs.sample.bayes import Likelihood, Prior
from gfs.sample.utils import load_data

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def infer_parameters(
    project: str,
    likelihood: Likelihood,
    prior: Prior,
    n_data_points: int,
    n_samples: int,
    data_file: str,
    output_file: str,
) -> None:
    logger.info(f"Load data from project={project}, file={data_file}")
    data = load_data(project=project, file=data_file)
    logger.info(f"Compute posterior with n_data_points={n_data_points}")
    posterior = prior.update(likelihood=likelihood, data=data[:n_data_points])
    logger.info(f"Generate histogram with n_samples={n_samples}")
    histogram = posterior.histogram(n_samples=n_samples)
    logger.info(f"Export histogram to file={output_file}")
    histogram.export(project=project, file=output_file, axis=0)
