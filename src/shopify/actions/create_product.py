"""Module for creating products in Shopify and saving data in the database"""

from psycopg import sql

from src.azure.azure_shopify_category_map import AZURE_SHOPIFY_CATEGORY_MAP
from src.db.models.product import ProductModel
from src.db.postgres import Database
from src.lib.logger import logger
from src.shopify.shopify import Shopify
from src.shopify.mutations import Mutations
from src.shopify.types.models.metafield import Metafield
from src.shopify.types.requests.product_create import (
    ProductCreateInput,
    ProductCreateResponse,
    OptionCreateInput,
)
from src.shopify.types.models.product import ProductStatus

class ProductCreateError(Exception):
    """Generic product creation error"""

def create_product(product: ProductModel) -> ProductModel:
    """Function for creating a product, adding media, and updating variants"""

    if product.shopify_product_id:
        return product

    (primary_category, secondary_category) = product.category.split(".")

    shopify_category = AZURE_SHOPIFY_CATEGORY_MAP[secondary_category]

    create_input = ProductCreateInput(
        category=shopify_category,
        descriptionHtml=product.description,
        handle=product.slug,
        productType=secondary_category,
        status=ProductStatus.draft,
        productOptions=[OptionCreateInput(name="Size")],
        tags=[
            primary_category,
            secondary_category,
            f"storage_{product.storage_climate}",
        ],
        title=product.name,
        vendor="Azure Standard",
        metafields=[Metafield(value=str(product.id))],
    )

    shopify = Shopify()

    product_create_response = ProductCreateResponse.model_validate(
        shopify.query_file(
            Mutations.product_create, {"product": create_input.model_dump()}
        )
    )

    if len(product_create_response.errors):
        logger.error(product_create_response.model_dump_json())
        raise ProductCreateError()

    if len(product_create_response.data.productCreate.userErrors):
        logger.error(product_create_response.model_dump_json())
        raise ProductCreateError()

    db = Database()

    db.batch_execute(
        sql.SQL("""
            UPDATE azure.products
            SET shopify_product_id = %(shopify_product_id)s
            WHERE id = %(product_id)s;
        """),
        [
            {
                "product_id": product.id,
                "shopify_product_id": product_create_response.data.productCreate.product.id,
            }
        ],
    )

    product.shopify_product_id = product_create_response.data.productCreate.product.id

    return product
