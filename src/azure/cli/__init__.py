from multiprocessing import Pool

from psycopg import sql, rows
import typer

from src.db.postgres import Database
from src.db.models.media import MediaModel

from .sync_to_shopify import sync_to_shopify
from .get_products_from_azure import get_products_from_azure
from .create_media_in_shopify import create_media_in_shopify
from .update_packaging import update_packaging
from .upload_images import upload_images

app = typer.Typer()


@app.command()
def shopify_sync():
    sync_to_shopify()


@app.command()
def create_media():
    create_media_in_shopify()


@app.command()
def scrape():
    get_products_from_azure()


@app.command()
def update_variants():
    update_packaging()


@app.command()
def upload_remaining_images():
    database = Database()

    media: MediaModel = database.fetchall(
        sql.SQL(
            """
                select * from (select distinct on (m.packaging_code)
                    m.* from azure.media as m
                join azure.packaging as pack on pack.code = m.packaging_code 
                join azure.products as p on p.id = pack.products_id
                where
                    p.shopify_product_id is not null and
                    pack.shopify_variant_id is not null
                order by m.packaging_code, m.shopify_media_id) where shopify_media_id is null limit 10;
            """
        ),
        {},
        rows.class_row(MediaModel),
    )

    number_of_images = len(media)
    print(len(media))
    with Pool(processes=7) as pool:
        for index, _ in enumerate(pool.imap_unordered(upload_images, media), 1):
            print(f"\rdone: {index / number_of_images:%}")


if __name__ == "__main__":
    app()

__all__ = ["app"]
