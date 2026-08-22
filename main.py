"""Main entrypoint for CLI tool"""

import typer

import src.azure.cli
import src.cli

app = typer.Typer()

# Cross-cutting commands live at the top level: `main sync-products`, etc.
for command in src.cli.app.registered_commands:
    app.registered_commands.append(command)

# Supplier sub-apps: `main azure scrape`, etc.
app.add_typer(src.azure.cli.app, name="azure")


if __name__ == "__main__":
    app()
