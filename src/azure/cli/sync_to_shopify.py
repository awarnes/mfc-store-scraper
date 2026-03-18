"""Action for pushing azure products from the DB to Shopify"""

import time
from typing import List


from rich.progress import Progress
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


def sync_to_shopify():
    logger.info("Syncing products to Shopify....")
    database = Database()

    products: List[ProductModel] = database.fetchall(
        sql.SQL("SELECT * FROM azure.products;"),
        {},
        rows.class_row(ProductModel),
    )

    with Progress() as progress:
        task = progress.add_task(
            f"Syncing {len(products)} products...", total=len(products)
        )

        failed_products: List[tuple[ProductModel, str]] = []

        for product in products:
            time.sleep(0.3)
            if product.shopify_product_id:
                progress.console.print("Product exists, skipping...")
                progress.advance(task)
                continue

            progress.console.print(f"Creating product in Shopify [{product.name}]")

            try:
                created_product = create_product(product)
            except ProductCreateError as err:
                failed_products.append(product, f"product error {err.message}")
                continue

            # logger.debug(created_product)

            try:
                created_variants = create_variants_for_product(created_product)
            except ProductVariantCreateError as err:
                failed_products.append(product, f"variant error {err.message}")

            # logger.debug(created_variants)

            progress.advance(task)
