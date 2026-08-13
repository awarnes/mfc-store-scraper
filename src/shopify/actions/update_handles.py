"""Action for updating Shopify product handles from Azure product data"""

from psycopg import sql

from src.db.postgres import Database
from src.lib.logger import logger
from src.shopify.shopify import Shopify ## client
from src.shopify.mutations import Mutations
from concurrent.futures import ThreadPoolExecutor, as_completed


class HandleUpdateError(Exception):
    """Raised when Shopify returns userErrors for a handle update."""


def _update_handle(shopify: Shopify, shopify_product_id: str, handle: str) -> None:
    resp = shopify.query_file(
        Mutations.product_handle_update,
        {"product": {"id": shopify_product_id, "handle": handle}},
    )

    data = resp.get("data", {}).get("productUpdate", {})
    user_errors = data.get("userErrors", []) or []
    top_errors = resp.get("errors", []) or []

    if top_errors or user_errors:
        raise HandleUpdateError(f"{top_errors or user_errors}")


def update_handles(
    product_id: int | None = None,
    max_workers: int = 5,
):
    """Update Shopify handles for Azure products in parallel batches.

    If product_id is provided, only that product is updated. Otherwise, all
    products with a shopify_product_id are updated.
    """
    logger.info("Starting Shopify handle update")

    database = Database()

    if product_id is not None:
        query = sql.SQL(
            """
            SELECT *
            FROM azure.product_handles
            WHERE id = %(id)s AND shopify_product_id IS NOT NULL
            LIMIT 1
            """
        )
        rows = database.fetchall(query, {"id": product_id})
    else:
        query = sql.SQL(
            """
            SELECT *
            FROM azure.product_handles
            WHERE shopify_product_id IS NOT NULL
            """
        )
        rows = database.fetchall(query, {})

    logger.info(f"Found {len(rows)} product(s) to update")

    shopify = Shopify()
    # Prime the token once so worker threads don't race on auth.
    shopify.get_token()

    updated = 0
    failed = 0

    def _task(row):
        shopify_product_id, handle = row[1], row[3]
        _update_handle(shopify, shopify_product_id, handle)
        return shopify_product_id, handle

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {pool.submit(_task, row): row for row in rows}
        for fut in as_completed(futures):
            row = futures[fut]
            try:
                shopify_product_id, handle = fut.result()
                logger.debug(f"Updated {shopify_product_id} → {handle}")
                updated += 1
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to update {row[1]}: {e}")
                failed += 1

    logger.success(f"Handle update complete: {updated} updated, {failed} failed")
