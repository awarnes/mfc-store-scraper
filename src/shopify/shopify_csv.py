"""
For managing Shopify CSV creation
"""

from dataclasses import dataclass
import csv
from datetime import datetime

@dataclass(kw_only=True)
class ShopifyProduct:
    title: str
    url_handle: str
    description: str
    vendor:str = "Montavilla Food Co-op"
    product_category:str
    type:str
    tags:str
    published:str = "FALSE"
    status:str = "Draft"
    sku:str
    barcode:str
    option1_name:str
    option1_value:str
    option2_name:str
    option2_value:str
    price:str
    compare_at_price:str
    cost_per_item:str
    charge_tax:str = "FALSE"
    inventory_tracker:str = "shopify"
    inventory_quantity:str
    continue_selling:str = "CONTINUE"
    weight_value:str
    weight_unit_display:str
    requires_shipping:str = "TRUE"
    fulfillment_service:str = "manual"
    product_image_url:str
    image_position:str
    image_alt_text:str
    variant_image_url:str
    gift_card:str
    seo_title:str
    seo_description:str

    def csv_format(self, fields=None):
        """
        Returns a formatted list for CSV writing
        Include only fields from fields array
        If fields = None include all fields
        """
        if fields is None:
            return self.__dict__.values()

        return [value for (key, value) in self.__dict__.items() if key in keys]

class ShopifyCsv:
    headers: List[str] = ["Title",
    "URL handle",
    "Description",
    "Vendor",
    "Product category",
    "Type",
    "Tags",
    "Published on online store",
    "Status",
    "SKU",
    "Barcode",
    "Option1 name",
    "Option1 value",
    "Option1 Linked To",
    "Option2 name",
    "Option2 value",
    "Option2 Linked To",
    "Option3 name",
    "Option3 value",
    "Option3 Linked To",
    "Price",
    "Compare-at price",
    "Cost per item",
    "Charge tax",
    "Tax code",
    "Inventory tracker",
    "Inventory quantity",
    "Continue selling when out of stock",
    "Weight value (grams)",
    "Weight unit for display",
    "Requires shipping",
    "Fulfillment service",
    "Product image URL",
    "Image position",
    "Image alt text",
    "Variant image URL",
    "Gift card",
    "SEO title",
    "SEO description"]

    def write_products(self, products: List[ShopifyProduct]):
        with open(f"{str(datetime.now()).replace(' ', 'T')}_shopify_upload.csv", "w", newline='') as csvfile:
            writer = csv.writer(csvfile, delimiter=',', quotechar='"',quoting=csv.QUOTE_MINIMAL)
            writer.writerow(self.headers)

            for product in products:
                writer.writerow(product.csv_format())
