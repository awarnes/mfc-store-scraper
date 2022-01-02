'''
File to store all constant values used in the project

Generally should be sorted/organized by use case
'''
PRODUCT_PAGE_SEARCH_SIZE: int = 25

SHOPIFY_STATUS_ACTIVE: str = 'active'
SHOPIFY_STATUS_DRAFT: str = 'draft'
SHOPIFY_IGNORE_WEIGHT: int = 0
SHOPIFY_IS_ONLINE_STORE: bool = True

SHOPIFY_VARIANT_FULFILLMENT_SERVICE_MANUAL: str = 'manual'
SHOPIFY_VARIANT_INVENTORY_POLICY_CONTINUE: str = 'continue'
SHOPIFY_VARIANT_INVENTORY_POLICY_DENY: str = 'deny'
SHOPIFY_VARIANT_INVENTORY_TRACKER_SHOPIFY: str = 'shopify'

SHOPIFY_CSV_FIELD_NAMES = {
    "handle": "Handle",
    "title": "Title",
    "body": "Body (HTML)",
    "vendor": "Vendor",
    "tags": "Tags",
    "published": "Published",
    "option1_name": "Option1 Name",
    "option1_value": "Option1 Value",
    "option2_name": "Option2 Name",
    "option2_value": "Option2 Value",
    "option3_name": "Option3 Name",
    "option3_value": "Option3 Value",
    "variant_sku": "Variant SKU",
    "variant_grams": "Variant Grams",
    "variant_inventory_tracker": "Variant Inventory Tracker",
    "variant_inventory_qty": "Variant Inventory Qty",
    "variant_inventory_policy": "Variant Inventory Policy",
    "variant_fulfillment_service": "Variant Fulfillment Service",
    "variant_price": "Variant Price",
    "variant_compare_at_price": "Variant Compare At Price",
    "variant_requires_shipping": "Variant Requires Shipping",
    "variant_taxable": "Variant Taxable",
    "variant_barcode": "Variant Barcode",
    "image_src": "Image Src",
    "image_position": "Image Position",
    "image_alt_text": "Image Alt Text",
    "gift_card": "Gift Card",
    "seo_title": "SEO Title",
    "seo_description": "SEO Description",
    "google_shopping_/_google_product_category": "Google Shopping / Google Product Category",
    "google_shopping_/_gender": "Google Shopping / Gender",
    "google_shopping_/_age_group": "Google Shopping / Age Group",
    "google_shopping_/_mpn": "Google Shopping / MPN",
    "google_shopping_/_adwords_grouping": "Google Shopping / AdWords Grouping",
    "google_shopping_/_adwords_labels": "Google Shopping / AdWords Labels",
    "google_shopping_/_condition": "Google Shopping / Condition",
    "google_shopping_/_custom_product": "Google Shopping / Custom Product",
    "google_shopping_/_custom_label_0": "Google Shopping / Custom Label 0",
    "google_shopping_/_custom_label_1": "Google Shopping / Custom Label 1",
    "google_shopping_/_custom_label_2": "Google Shopping / Custom Label 2",
    "google_shopping_/_custom_label_3": "Google Shopping / Custom Label 3",
    "google_shopping_/_custom_label_4": "Google Shopping / Custom Label 4",
    "variant_image": "Variant Image",
    "variant_weight_unit": "Variant Weight Unit",
    "variant_tax_code": "Variant Tax Code",
    "cost_per_item": "Cost per item",
    "status": "Status",
    "standard_product_type": "Standard Product Type",
    "custom_product_type": "Custom Product Type"
}
