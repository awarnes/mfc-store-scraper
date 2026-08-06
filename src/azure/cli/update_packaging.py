"""Action for updating prices of products in Shopify"""

from src.db.models.packaging import PackagingModel
from src.lib.logger import logger
from src.shopify.actions import update_variant, ProductVariantUpdateError


def update_packaging(packaging: PackagingModel):
    try:
        if not packaging.shopify_variant_id:
            logger.info("Variant does not exist, cannot update...")
            return

        logger.debug(f"Updating variant in Shopify [{packaging.shopify_variant_id}]")

        try:
            updated_variant = update_variant(packaging)
        except ProductVariantUpdateError as err:
            logger.error((packaging, f"pack error {err.message}"))
            return
    except Exception as err:
        print(err)

    logger.debug(f"Successfully updated packaging {packaging.id}")
