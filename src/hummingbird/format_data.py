'''
Formatting functions for Hummingbird Wholesale data retrieval
'''
import math
import re

from bs4 import BeautifulSoup

from src.hummingbird.constants import MULTI_PACK_CONVERTER, HUMMINGBIRD_WHOLESALE_VENDOR
from src.utils import description_filter_text, format_image_src
from src.constants import (
    SHOPIFY_STATUS_DRAFT,
    SHOPIFY_IGNORE_WEIGHT,
    SHOPIFY_IS_ONLINE_STORE,
    SHOPIFY_VARIANT_FULFILLMENT_SERVICE_MANUAL,
    SHOPIFY_VARIANT_INVENTORY_POLICY_CONTINUE,
    SHOPIFY_VARIANT_INVENTORY_TRACKER_SHOPIFY
)

# pylint: disable=consider-using-f-string

def format_products(product_data):
    '''
    Formats product data from Hummingbird Wholesale for import into Shopify store
    '''
    # pylint: disable=too-many-statements
    formatted_products = []

    for product in product_data:
        # BASE PRODUCT
        new_product = {}
        multi_pack = False
        multi_pack_amount = None

        new_product['Handle'] = product['id']
        new_product['Title'] = product['title']

        description_html = product['description']
        description_soup = BeautifulSoup(description_html, 'html.parser')
        new_product['Body (HTML)'] = ''.join(
            ['<h4>From Hummingbird Wholesale</h4>'] +
            [
                re.sub('\n', '', str(tag))
                for tag in description_soup.find_all(description_filter_text)
            ]
        )

        new_product['Vendor'] = HUMMINGBIRD_WHOLESALE_VENDOR
        new_product['Tags'] = ','.join([tag.lower() for tag in product['tags']])
        new_product['Published'] = SHOPIFY_IS_ONLINE_STORE

        if len(product['options']) > 1:
            print(
                'NEW OPTION(S) REQUIRED: {0} on {1}//{2}'.format(
                    product['options'], new_product['Handle'], new_product['Title']
                )
            )

        primary_variant = product['variants'][0]

        new_product['Option1 Name'] = product['options'][0].capitalize()

        # Check for a multi-pack product
        if is_multi_pack(primary_variant):
            new_product['Option1 Value'] = MULTI_PACK_CONVERTER[primary_variant['option1']]
            multi_pack = True
            multi_pack_amount = get_multi_pack_amount(primary_variant)
        else:
            new_product['Option1 Value'] = primary_variant['option1']

        new_product['Variant SKU'] = primary_variant['sku']

        new_product['Variant Grams'] = 0
        new_product['Variant Inventory Policy'] = 'continue'
        new_product['Variant Fulfillment Service'] = 'manual'
        new_product['Variant Price'] = get_product_price(primary_variant['price'], multi_pack_amount)
        new_product['Variant Inventory Tracker'] = 'shopify' if multi_pack else None

        new_product['Image Src'] = format_image_src(product['featured_image'])

        new_product['Variant Image'] = new_product['Image Src']

        new_product['Image Alt Text'] = new_product['Title']

        new_product['Status'] = SHOPIFY_STATUS_DRAFT

        formatted_products.append(new_product)

        # PRODUCT VARIANTS
        for variant in product['variants'][1:]:
            new_variant = {}
            multi_pack = False
            multi_pack_amount = None

            new_variant['Handle'] = new_product['Handle']

            new_variant['Published'] = SHOPIFY_IS_ONLINE_STORE
            new_variant['Option1 Name'] = new_product['Option1 Name']

            # Check for a multi-pack product
            if is_multi_pack(variant):
                new_variant['Option1 Value'] = MULTI_PACK_CONVERTER[variant['option1']]
                multi_pack = True
                multi_pack_amount = get_multi_pack_amount(variant)
            else:
                new_variant['Option1 Value'] = variant['option1']

            new_variant['Variant SKU'] = variant['sku']

            new_variant['Variant Grams'] = SHOPIFY_IGNORE_WEIGHT
            new_variant['Variant Inventory Policy'] = SHOPIFY_VARIANT_INVENTORY_POLICY_CONTINUE
            new_variant['Variant Fulfillment Service'] = SHOPIFY_VARIANT_FULFILLMENT_SERVICE_MANUAL

            new_variant['Variant Price'] = get_product_price(variant['price'], multi_pack_amount)
            new_variant['Variant Inventory Tracker'] = \
                SHOPIFY_VARIANT_INVENTORY_TRACKER_SHOPIFY if multi_pack else None

            if variant['featured_image']:
                new_variant['Variant Image'] = variant['featured_image']['src']

            new_variant['Status'] = SHOPIFY_STATUS_DRAFT

            formatted_products.append(new_variant)

    return formatted_products

def is_multi_pack(variant):
    '''
    Checks if a product is considered a multi_pack product.
    Must have an `option1` key that matches the regex below
    '''
    match = re.match(r'.*\d+\s?x.*', variant['option1'])
    return match[0] in MULTI_PACK_CONVERTER if match else False

def get_multi_pack_amount(variant):
    '''
    Returns the multi_pack_amount (_6_ x 6) for a given product (variant).
    Must have an `option1` key that matches the regex below
    '''
    return int(re.search(r'\d+(?=\s?x)', variant['option1'])[0])

def get_product_price(price, multi_pack_amount=None):
    '''
    Returns the proper price.
    If there are partial pennies, then we should always round up.
    '''
    if multi_pack_amount:
        if price % multi_pack_amount:   
            price = (math.floor(price / multi_pack_amount) + 1)
        else:
            price /= multi_pack_amount

    return price / 100
