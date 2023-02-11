import click

from gfs.sample.infer import mock_infer


@click.group()
def cli() -> None:
    pass


@cli.command()
@click.option("--config", type=str, required=True)
def infer(config: str) -> None:
    mock_infer(config=config)
