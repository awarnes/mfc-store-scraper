"""Action for pushing azure products from the DB to Shopify"""

import json
from multiprocessing import Pool
from typing import List

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

def sync_to_shopify(products: List[ProductModel]):
    failed_products: List[tuple[ProductModel, str]] = []

    try: 
        for product in products:
            if product.shopify_product_id:
                logger.info("Product exists, skipping...")
                continue

            logger.info(f"Creating product in Shopify [{product.name}]")

            try:
                created_product = create_product(product)
            except ProductCreateError as err:
                failed_products.append((product, f"product error {err.message}"))
                continue

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
    finally:
        with open('errors.json', 'w+', encoding='utf-8') as f:
            logger.error(json.dumps(failed_products))
            f.write(json.dumps(failed_products))


if __name__ == '__main__':
    logger.info("Syncing products to Shopify....")
    database = Database()

    products: List[ProductModel] = database.fetchall(
        sql.SQL("SELECT * FROM azure.products WHERE shopify_product_id IS NULL;"),
        {},
        rows.class_row(ProductModel),
    )

    with Pool(processes=5) as pool:
        pool.imap(sync_to_shopify, products, 10)