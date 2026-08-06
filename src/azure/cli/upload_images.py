"""Temp CLI command to update remaining images in shopify"""

from psycopg import rows, sql

from src.db.models.media import MediaModel
from src.db.postgres import Database
from src.db.models.product import ProductModel
from src.db.models.packaging import PackagingModel
from src.lib.logger import logger
from src.shopify.actions import create_media, ProductVariantUpdateError
from src.shopify.mutations import Mutations
from src.shopify.shopify import Shopify
from src.shopify.types.models.metafield import Metafield
from src.shopify.types.requests.product_variants_bulk_input import (
    ProductVariantsBulkUpdateResponse,
)


def upload_images(media: MediaModel):
    if media.shopify_media_id:
        logger.info(f"Image already uploaded for {media.packaging_code}")

    shopify_media: MediaModel = create_media(media)

    if not shopify_media:
        logger.error('Unable to create media')
        return

    db = Database()

    variant = PackagingModel.model_validate(
        db.fetchone(
            sql.SQL("""SELECT * FROM azure.packaging WHERE code = %(code)s LIMIT 1;"""),
            {"code": media.packaging_code},
            rows.class_row(PackagingModel),
        )
    )

    product = ProductModel.model_validate(
        db.fetchone(
            sql.SQL(
                """SELECT * FROM azure.products WHERE id = %(product_id)s LIMIT 1;"""
            ),
            {"product_id": variant.products_id},
            rows.class_row(ProductModel),
        )
    )

    packaging_input = {
        "id": variant.shopify_variant_id,
        "mediaId": shopify_media.shopify_media_id,
        "metafields": [Metafield(value=str(variant.id)).model_dump()],
    }

    shopify = Shopify()

    raw_variant_update_response = shopify.query_file(
        Mutations.product_variants_bulk_update,
        {
            "productId": product.shopify_product_id,
            "variants": [packaging_input],
            "namespace": "internal",
            "key": "id",
        },
    )

    logger.info(raw_variant_update_response)

    product_variants_bulk_response = ProductVariantsBulkUpdateResponse.model_validate(
        raw_variant_update_response
    )

    if len(product_variants_bulk_response.errors):
        logger.error(product_variants_bulk_response.model_dump_json())
        raise ProductVariantUpdateError()

    if len(product_variants_bulk_response.data.productVariantsBulkUpdate.userErrors):
        logger.error(product_variants_bulk_response.model_dump_json())
        raise ProductVariantUpdateError()

    return product_variants_bulk_response
