"""Action for pushing dirty azure.packaging rows to Shopify as variant updates."""

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List

from psycopg import sql

from src.db.postgres import Database, MARKUP_PERCENTAGE
from src.lib.logger import logger
from src.shopify.mutations import Mutations
from src.shopify.queries import Queries
from src.shopify.shopify import Shopify


class VariantUpdateError(Exception):
    """Raised when Shopify returns userErrors for a variant update."""


# Row shape returned by the dirty query.
# (packaging_id, packaging_code, shopify_variant_id, shopify_product_id, retail_dollars)
DirtyRow = tuple


def _fetch_dirty_rows(
    database: Database,
    packaging_code: str | None,
    product_id: int | None,
    limit: int | None = None,
) -> List[DirtyRow]:
    base = """
        WITH latest_price AS (
            SELECT DISTINCT ON (packaging_code)
                packaging_code, retail_dollars, created_at
            FROM azure.prices
            ORDER BY packaging_code, created_at DESC
        )
        SELECT
            pack.id,
            pack.code,
            pack.shopify_variant_id,
            prod.shopify_product_id,
            lp.retail_dollars as retail_dollars,
            pack.stock,
            pack.shopify_inventory_item_id
        FROM azure.packaging pack
        JOIN azure.products prod ON prod.id = pack.products_id
        LEFT JOIN latest_price lp ON lp.packaging_code = pack.code
        WHERE pack.shopify_variant_id IS NOT NULL
          AND prod.shopify_product_id IS NOT NULL
          AND lp.retail_dollars IS NOT NULL
    """

    if packaging_code is not None:
        query = sql.SQL(base + " AND pack.code = %(code)s")
        return database.fetchall(query, {"code": packaging_code})

    if product_id is not None:
        query = sql.SQL(base + " AND prod.id = %(product_id)s")
        return database.fetchall(query, {"product_id": product_id})

    query = sql.SQL(
        base
        + """
          AND (
            pack.shopify_updated_at IS NULL
            OR pack.shopify_updated_at < GREATEST(pack.updated_at, lp.created_at)
          ) LIMIT %(limit)s
        """
    )
    return database.fetchall(query, { "limit": limit })

def _get_primary_location_id(shopify: Shopify) -> str:
    resp = shopify.query_file(Queries.location_primary, {})
    return resp["data"]["locations"]["nodes"][0]["id"]


def _resolve_inventory_item_ids(
    shopify: Shopify,
    database: Database,
    rows: list[DirtyRow],
) -> dict[str, str]:
    """Return {shopify_variant_id: shopify_inventory_item_id}, populating
    azure.packaging for any rows that were missing it."""
    known = {r[2]: r[6] for r in rows if r[6]}
    missing_variant_ids = [r[2] for r in rows if not r[6]]

    if not missing_variant_ids:
        return known

    CHUNK = 250
    updates = []

    for i in range(0, len(missing_variant_ids), CHUNK):
        batch = missing_variant_ids[i : i + CHUNK]
        resp = shopify.query_file(
            Queries.inventory_items_by_variants,
            {"ids": batch},
        )
        for node in resp["data"]["nodes"]:
            if not node:
                continue
            variant_id = node["id"]
            item_id = node["inventoryItem"]["id"]
            known[variant_id] = item_id
            updates.append({"variant_id": variant_id, "item_id": item_id})

    if updates:
        database.batch_execute(
            sql.SQL("""
                UPDATE azure.packaging
                SET shopify_inventory_item_id = %(item_id)s
                WHERE shopify_variant_id = %(variant_id)s
            """),
            updates,
        )

    return known


def _update_product_variants(
    shopify: Shopify,
    shopify_product_id: str,
    variants_payload: list[dict],
) -> None:
    resp = shopify.query_file(
        Mutations.product_variants_bulk_update,
        {
            "productId": shopify_product_id,
            "variants": variants_payload,
            "namespace": "internal",
            "key": "id",
        },
    )

    data = resp.get("data", {}).get("productVariantsBulkUpdate", {}) or {}
    user_errors = data.get("userErrors", []) or []
    top_errors = resp.get("errors", []) or []

    if top_errors or user_errors:
        raise VariantUpdateError(f"{top_errors or user_errors}")

def _set_on_hand(
    shopify: Shopify,
    location_id: str,
    entries: list[dict],
) -> None:
    resp = shopify.query_file(
        Mutations.inventory_set_on_hand,
        {
            "input": {
                "reason": "correction",
                "setQuantities": [
                    {
                        "inventoryItemId": e["inventory_item_id"],
                        "locationId": location_id,
                        "quantity": int(e["quantity"]),
                    }
                    for e in entries
                ],
            }
        },
    )
    data = resp.get("data", {}).get("inventorySetOnHandQuantities", {}) or {}
    user_errors = data.get("userErrors", []) or []
    top_errors = resp.get("errors", []) or []
    if top_errors or user_errors:
        raise VariantUpdateError(f"{top_errors or user_errors}")


def update_variants(
    packaging_code: str | None = None,
    product_id: int | None = None,
    max_workers: int = 5,
    limit: int | None = None,
):
    """Push variant-level updates (price) to Shopify for any dirty packaging rows.

    Dirty = shopify_variant_id IS NOT NULL AND
            shopify_updated_at < GREATEST(packaging.updated_at, latest_price.created_at).
    """
    logger.info("Starting Shopify variant update")

    database = Database()
    rows = _fetch_dirty_rows(database, packaging_code, product_id, limit)
    logger.info(f"Found {len(rows)} variant(s) to update")
    if not rows:
        return

    shopify = Shopify()
    shopify.get_token()  # Prime token so worker threads don't race on auth.
    location_id = _get_primary_location_id(shopify)
    inventory_item_ids = _resolve_inventory_item_ids(shopify, database, rows)

    # Group by shopify_product_id so we do one bulk mutation per product.
    grouped: dict[str, list[DirtyRow]] = defaultdict(list)
    for row in rows:
        grouped[row[3]].append(row)

    logger.info(f"Grouped into {len(grouped)} product batch(es)")

    updated = 0
    failed = 0


    def _task(shopify_product_id: str, product_rows: list[DirtyRow]):
        ## r[4] is the retail price
        variants_payload = [
            {
                "id": r[2],
                "price": f"{round(float(r[4]) / (1 - (MARKUP_PERCENTAGE/100)), 2):.2f}",
                "inventoryPolicy": "DENY",  # or "CONTINUE"
                "inventoryItem": { "cost": f"{round(float(r[4]), 2):.2f}" }
            }
            for r in product_rows
        ]
        _update_product_variants(shopify, shopify_product_id, variants_payload)

        # 2) Stock (skip rows we couldn't resolve, or with null stock)
        stock_entries = [
            {
                "inventory_item_id": inventory_item_ids[r[2]],
                "quantity": r[5],
            }
            for r in product_rows
            if r[5] is not None and inventory_item_ids.get(r[2])
        ]
        if stock_entries:
            _set_on_hand(shopify, location_id, stock_entries)

        return product_rows

    with ThreadPoolExecutor(max_workers=max_workers) as pool:
        futures = {
            pool.submit(_task, spid, product_rows): (spid, product_rows)
            for spid, product_rows in grouped.items()
        }
        for fut in as_completed(futures):
            spid, product_rows = futures[fut]
            try:
                fut.result()
                database.batch_execute(
                    sql.SQL(
                        """
                        UPDATE azure.packaging
                        SET shopify_updated_at = now()
                        WHERE id = %(id)s
                        """
                    ),
                    [{"id": r[0]} for r in product_rows],
                )
                logger.debug(
                    f"Updated {len(product_rows)} variant(s) for product {spid}"
                )
                updated += len(product_rows)
            except Exception as e:  # noqa: BLE001
                logger.error(f"Failed to update product {spid}: {e}")
                failed += len(product_rows)

    logger.success(f"Variant update complete: {updated} updated, {failed} failed")
