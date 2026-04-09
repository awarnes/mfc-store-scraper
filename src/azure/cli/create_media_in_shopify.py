"""Action for Azure media from the DB to Shopify"""

import json
from typing import List

from rich.progress import MofNCompleteColumn, Progress, SpinnerColumn, TimeElapsedColumn
from psycopg import sql, rows

from src.db.postgres import Database
from src.db.models.media import MediaModel
from src.lib.logger import logger
from src.shopify.actions import (
    create_media,
)

def create_media_in_shopify():
    logger.info("Creating media to Shopify....")
    database = Database()

    media: List[MediaModel] = database.fetchall(
        sql.SQL("SELECT * FROM azure.media WHERE shopify_media_id IS NULL;"),
        {},
        rows.class_row(MediaModel),
    )

    with Progress(
        SpinnerColumn(),
        *Progress.get_default_columns(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ) as progress:
        task = progress.add_task(
            f"Syncing {len(media)} products...", total=len(media)
        )

        failed_products: List[tuple[MediaModel, str]] = []
        try: 
            for image in media:
                if image.shopify_media_id:
                    progress.console.print("Media exists, skipping...")
                    progress.advance(task)
                    continue

                progress.console.print(f"Creating Media in Shopify [{image.file_name}]")

                try:
                    create_media(image)
                except Exception as err:
                    failed_products.append((image, f"unknown error {err}"))

                progress.advance(task)
        finally:
            with open('errors.json', 'w+', encoding='utf-8') as f:
                logger.error(json.dumps(failed_products))
                f.write(json.dumps(failed_products))
