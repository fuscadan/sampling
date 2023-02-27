from gfs.sample.bayes import Likelihood, Prior
from gfs.sample.utils import load_data


def infer_parameters(
    project: str,
    likelihood: Likelihood,
    prior: Prior,
    n_data_points: int,
    n_samples: int,
    data_file: str,
    output_file: str,
) -> None:
    data = load_data(project=project, file=data_file)
    posterior = prior.update(likelihood=likelihood, data=data[:n_data_points])
    histogram = posterior.histogram(n_samples=n_samples)
    histogram.export(project=project, file=output_file, axis=0)
