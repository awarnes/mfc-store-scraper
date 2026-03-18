from pydantic import BaseModel


class Metafield(BaseModel):
    """
    Can be used to associate any custom data with a product or variant

    We primarily use it to add our internal database ID into the Shopify model
    """

    namespace: str = "internal"
    key: str = "id"
    # See available types here: https://shopify.dev/docs/apps/build/metafields/list-of-data-types
    type: str = "number_integer"
    value: str  # shopify always stores as string
