import typer

from .sync_to_shopify import sync_to_shopify
from .get_products_from_azure import get_products_from_azure

app = typer.Typer()


@app.command()
def shopify_sync():
    sync_to_shopify()


@app.command()
def scrape():
    get_products_from_azure()


if __name__ == "__main__":
    app()

__all__ = ["app"]
