"""Module for managing media creation in Shopify and saving into database"""

from tempfile import TemporaryDirectory

from psycopg import rows, sql

from src.db.models.media import MediaModel
from src.db.postgres import Database
from src.lib.logger import logger
from src.shopify.media_manager import MediaManager


def create_media(media_record: MediaModel) -> MediaModel:
    """Create a media in Shopify that can be associated with a product"""

    if media_record.shopify_media_id:
        logger.debug("Media already uploaded, skipping...")
        return media_record

    media_manager = MediaManager()

    with TemporaryDirectory() as tmpdir:
        path = media_manager.download(
            media_record.file_name, media_record.original_url, tmpdir
        )

        staged_response = media_manager.generate_staged_upload(media_record.file_name)

        target = (
            staged_response.get("data")
            .get("stagedUploadsCreate")
            .get("stagedTargets")[0]
        )

        media_manager.upload_image_to_staged_target(target, path)

        created_file = media_manager.create_file(target["resourceUrl"])

        shopify_media_id = (
            created_file.get("data").get("fileCreate").get("files")[0].get("id")
        )

        media_update_query = sql.SQL("""
            UPDATE azure.media
            SET shopify_media_id = %(shopify_media_id)s
            WHERE id = %(id)s;
        """)

        database = Database()

        database.batch_execute(
            media_update_query,
            [{"id": media_record.id, "shopify_media_id": shopify_media_id}],
        )

        return database.fetchone(
            sql.SQL("SELECT * FROM azure.media WHERE id = %(id)s;"),
            {"id": media_record.id},
            rows.class_row(MediaModel),
        )
