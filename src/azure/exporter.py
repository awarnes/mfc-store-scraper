"""
Module for exporting Azure Standard data for importing into Shopify
"""

from src.shopify.shopify_csv import ShopifyProduct

# """
# Title,URL handle,Description,Vendor,Product category,Type,Tags,Published on online store,Status,SKU,Barcode,Option1 name,Option1 value,Option1 Linked To,Option2 name,Option2 value,Option2 Linked To,Option3 name,Option3 value,Option3 Linked To,Price,Compare-at price,Cost per item,Charge tax,Tax code,Inventory tracker,Inventory quantity,Continue selling when out of stock,Weight value (grams),Weight unit for display,Requires shipping,Fulfillment service,Product image URL,Image position,Image alt text,Variant image URL,Gift card,SEO title,SEO description
# """

# "Title",
# "URL handle",
# "Description",
# "Vendor",
# "Product category",
# "Type",
# "Tags",
# "Published on online store",
# "Status",
# "SKU",
# "Barcode",
# "Option1 name",
# "Option1 value",
# "Option1 Linked To",
# "Option2 name",
# "Option2 value",
# "Option2 Linked To",
# "Option3 name",
# "Option3 value",
# "Option3 Linked To",
# "Price",
# "Compare-at price",
# "Cost per item",
# "Charge tax",
# "Tax code",
# "Inventory tracker",
# "Inventory quantity",
# "Continue selling when out of stock",
# "Weight value (grams)",
# "Weight unit for display",
# "Requires shipping",
# "Fulfillment service",
# "Product image URL",
# "Image position",
# "Image alt text",
# "Variant image URL",
# "Gift card",
# "SEO title",
# "SEO description"


class AzureExporter:
    def get_products(self):
        pass
        # connect to db
        # get products
        # for each product get packaging and most recent price
        # return shopify_formatted products

    def shopify_format(self, product):
        """Format a product for Shopify"""

        return ShopifyProduct(
            title="",
            url_handle="",
            description="",
            product_category="",
            type="",
            tags="",
            sku="",
            barcode="",
            option1_name="",
            option1_value="",
            option2_name="",
            option2_value="",
            price="",
            compare_at_price="",
            cost_per_item="",
            inventory_quantity="",
            weight_value="",
            weight_unit_display="",
            product_image_url="",
            image_position="",
            image_alt_text="",
            variant_image_url="",
            gift_card="",
            seo_title="",
            seo_description="",
        )
