"""Module for managing media creation in Shopify and saving into database"""

from tempfile import TemporaryDirectory

from psycopg import sql

from src.db.models.media import MediaModel
from src.db.postgres import Database
from src.shopify.media_manager import MediaManager
from src.lib.logger import logger


def create_media(media_record: MediaModel):
    """Create a media in Shopify that can be associated with a product"""
    if media_record.shopify_media_id:
        logger.debug("Media already uploaded, skipping...")
        return media_record

    media_manager = MediaManager()

    with TemporaryDirectory() as tmpdir:
        # Download the file from the original_url to a temporary local file

        path = media_manager.download(
            media_record.file_name, media_record.original_url, tmpdir
        )
        logger.debug(path)

        # Create a staged target for upload into Shopify
        staged_response = media_manager.generate_staged_upload(media_record.file_name)
        logger.debug(staged_response)

        target = (
            staged_response.get("data")
            .get("stagedUploadsCreate")
            .get("stagedTargets")[0]
        )
        # Upload file to staged target
        logger.debug(media_manager.upload_image_to_staged_target(target, path))

        # Create the file in the shopify backend of the uploaded image
        created_file = media_manager.create_file(target["resourceUrl"])
        logger.debug(created_file)

        shopify_media_id = (
            created_file.get("data").get("fileCreate").get("files")[0].get("id")
        )

        # Insert the created file ID into the database
        media_update_query = sql.SQL("""
            UPDATE azure.media
            SET shopify_media_id = %(shopify_media_id)s
            WHERE id = %(id)s;
        """)

        database = Database()

        logger.info("Inserting media...")
        Database().batch_execute(
            media_update_query,
            [{"id": media_record.id, "shopify_media_id": shopify_media_id}],
        )

        return database.fetchone(
            sql.SQL("SELECT * FROM azure.media WHERE id = %(id)s;"),
            {"id": media_record.id},
        )
