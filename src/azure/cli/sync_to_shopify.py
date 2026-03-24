"""Action for pushing azure products from the DB to Shopify"""

import json
from typing import List

from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn
from psycopg import sql, rows

from src.db.postgres import Database
from src.db.models.product import ProductModel
from src.lib.logger import logger
from src.shopify.actions import (
    create_product,
    ProductCreateError,
    create_variants_for_product,
    ProductVariantCreateError,
)
from src.shopify.media_manager import StagedUploadFailedError, MediaDownloadFailedError

def sync_to_shopify():
    logger.info("Syncing products to Shopify....")
    database = Database()

    products: List[ProductModel] = database.fetchall(
        sql.SQL("SELECT * FROM azure.products;"),
        {},
        rows.class_row(ProductModel),
    )

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            f"Syncing {len(products)} products...", total=len(products)
        )

        failed_products: List[tuple[ProductModel, str]] = []
        try: 
            for product in products:
                if product.shopify_product_id:
                    progress.console.print("Product exists, skipping...")
                    progress.advance(task)
                    continue

                progress.console.print(f"Creating product in Shopify [{product.name}]")

                try:
                    created_product = create_product(product)
                except ProductCreateError as err:
                    failed_products.append((product, f"product error {err.message}"))
                    continue

                # logger.debug(created_product)

                try:
                    created_variants = create_variants_for_product(created_product)
                except ProductVariantCreateError as err:
                    failed_products.append((product, f"variant error {err.message}"))
                except MediaDownloadFailedError as err:
                    failed_products.append((product, f"download error {err.message}"))
                except StagedUploadFailedError as err:
                    failed_products.append((product, f"upload error {err.message}"))
                except Exception as err:
                    failed_products.append((product, f"unknown error {err}"))

                # logger.debug(created_variants)

                progress.advance(task)
        finally:
            with open('errors.json', 'w+', encoding='utf-8') as f:
                logger.error(json.dumps(failed_products))
                f.write(json.dumps(failed_products))
