"""Main CLI entry point"""

from psycopg import sql

from src.azure.scraper import AzureScraper
from src.db.postgres import Database
from src.lib.logger import logger

if __name__ == "__main__":
    logger.info("Starting Azure product scraper")

    scraper = AzureScraper()

    logger.info("Retrieving all products...")
    all_products = scraper.get_all_products()
    logger.debug(f"Retrieved {len(all_products)} products")

    logger.info("Formatting products...")
    (formatted_products, formatted_packaging, formatted_prices, formatted_media) = (
        scraper.format_products(all_products)
    )
    logger.debug(
        f"Formatted {len(formatted_products)} products, \
        {len(formatted_packaging)} packaging, {len(formatted_prices)} prices"
    )

    database = Database()
    logger.info("Connected to database")

    # pylint: disable=line-too-long
    product_query = sql.SQL(
        """
        INSERT INTO azure.products (id, name, short_description, description, slug, storage_climate, unshippable_regions, brand, substitutions, category)
        VALUES
        (%(id)s,%(name)s,%(short_description)s,%(description)s,%(slug)s,%(storage_climate)s,%(unshippable_regions)s,%(brand)s,%(substitutions)s, %(category)s)
        ON CONFLICT(id)
        DO UPDATE SET
            name = EXCLUDED.name,
            short_description = EXCLUDED.short_description,
            description = EXCLUDED.description,
            slug = EXCLUDED.slug,
            storage_climate = EXCLUDED.storage_climate,
            unshippable_regions = EXCLUDED.unshippable_regions,
            brand = EXCLUDED.brand,
            substitutions = EXCLUDED.substitutions,
            category = EXCLUDED.category,
            updated_at = now()
    """
    )

    logger.info("Inserting products...")
    database.batch_execute(product_query, formatted_products)
    logger.info(f"Inserted {len(formatted_products)} products")

    packaging_query = sql.SQL(
        """
        INSERT INTO azure.packaging (products_id, code, size, weight, stock, rewards_enabled, freight_handling_required, tags, primary_category,favorites,next_purchase_arrival)
        VALUES (%(products_id)s,%(code)s,%(size)s,%(weight)s,%(stock)s,%(rewards_enabled)s,%(freight_handling_required)s,%(tags)s,%(primary_category)s,%(favorites)s,%(next_purchase_arrival)s)
        ON CONFLICT(products_id, code)
        DO UPDATE SET
            size = EXCLUDED.size,
            weight = EXCLUDED.weight,
            stock = EXCLUDED.stock,
            rewards_enabled = EXCLUDED.rewards_enabled,
            freight_handling_required = EXCLUDED.freight_handling_required,
            tags = EXCLUDED.tags,
            primary_category = EXCLUDED.primary_category,
            favorites = EXCLUDED.favorites,
            next_purchase_arrival = EXCLUDED.next_purchase_arrival;
    """
    )

    logger.info("Inserting packaging...")
    database.batch_execute(packaging_query, formatted_packaging)
    logger.info(f"Inserted {len(formatted_packaging)} packaging records")

    # pylint: disable=fixme
    # TODO: Only insert prices for existing packages
    prices_query = sql.SQL(
        """
        INSERT INTO azure.prices (packaging_code, retail_dollars, retail_unit, wholesale_dollars, wholesale_unit)
        VALUES (%(packaging_code)s,%(retail_dollars)s,%(retail_unit)s,%(wholesale_dollars)s,%(wholesale_unit)s);
    """
    )

    logger.info("Inserting prices...")
    database.batch_execute(prices_query, formatted_prices)
    logger.info(f"Inserted {len(formatted_prices)} price records")

    media_query = sql.SQL(
        """
        INSERT INTO azure.media (packaging_code, original_url, file_name)
        VALUES (%(packaging_code)s,%(original_url)s, %(file_name)s);
    """
    )

    logger.info("Inserting media...")
    database.batch_execute(media_query, formatted_media)
    logger.info(f"Inserted {len(formatted_media)} media records")

    logger.success("Azure product scraper completed successfully")
