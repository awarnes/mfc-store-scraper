"""Main entrypoint for CLI tool"""

import typer

import src.azure.cli
from src.lib.logger import logger

app = typer.Typer()

app.add_typer(src.azure.cli.app, name="azure")


if __name__ == "__main__":
    app()
