'''
File to store all constant values used in the project

Generally should be sorted/organized by use case
'''
HUMMINGBIRD_WHOLESALE_BASE_URL: str = 'https://hummingbirdwholesale.com'
PRODUCT_PAGE_SEARCH_SIZE: int = 25
ALL_PRODUCTS_URL: str = '/collections/all'

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

MULTI_PACK_CONVERTER = {
    'Case of 6 x 5.5 lb / 1/2 gal Jars': '5.5 lb / 1/2 gal Jar',
    'case of 6 x 51 oz can': '51 oz can',
    'Case of 12 x 32 oz round glass decanters': '32 oz round glass decanter',
    'Case of 12 x 1lb Jars': '1 lb jar',
    'case of 8 x 2.5 oz bags': '2.5 oz bag',
    'case of 10 x 2 lb bags': '2 lb bag',
    'Case of 12 x 12 oz flat glass bottles': '12 oz flat glass bottle',
    'Case of 12 x 3 oz tins': '3 oz tin',
    '10 x  ½ oz Stand-Up Pouch': '½ oz Stand-Up Pouch',
    'Case of 12 x 5 oz glass bottles': '5 oz glass bottle',
    'case of 6 x 1 lb bags': '1 lb bag',
    'case of 12 x 1 lb jar': '1 lb jar',
    '16 lb case (4x4lb bags)': '4 lb bag',
    '20 lb case (4x5 lb bag)': '5 lb bag',
    'Case of 12 x 1lb jars': '1 lb jar',
    'Case of 12 x 16 fl oz Jar': '16 fl oz jar',
    '10 x  ½ oz Stand-up Pouch': '½ oz Stand-up Pouch',
    '6 x 6 oz bags': '6 oz bag',
    '4 x 5 lb bags': '5 lb bag',
    'case of 6 x 6 oz bags': '6 oz bag',
    'case of 6 x 1/2 lb bags': '1/2 lb bag',
    'Case of 12 x 16 oz round glass decanters': '16 oz round glass decanter',
    'case of 6 x 12oz bags': '12 oz bag',
    'Case of 12 x 1 lb Jar': '1 lb jar',
    'Case of 12 x 1 lb jars': '1 lb jar',
    '20 lb case (4x5lb bags)': '5 lb bag',
    'Case of 6 x 5.5 lb /1/2 gal Jars': '5.5 lb / 1/2 gal Jar',
    'Case of 6 x 1/2 gal Glass Jugs': '1/2 gal glass jug',
    '12 x 8.5 fl oz bottles': '8.5 fl oz bottle',
    'case of 10 x 4 oz bag': '4 oz bag',
    'Case of 12 x 2 oz tins': '2 oz tin',
    'Case of 12 x 1 lb Jars': '1 lb jar'
}