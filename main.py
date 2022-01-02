'''
Primary entry point for store scraping code.
'''

import csv
import json
import re
import requests

from bs4 import BeautifulSoup

import src.constants as const
import src.utils as utils

# pylint: disable=consider-using-f-string

with open('./hummingbird_products.json', 'w', encoding='utf8') as jsonfile:
    print('Retrieving product data...')
    product_data, missing_products = all_product_data(all_product_ids(const.ALL_PRODUCTS_URL))
    print('Saving all products to file...')
    json.dump(product_data, jsonfile)
    print('Products saved to file...')
    if missing_products:
        print('~~~Some Product IDs are Missing From Product Data!!~~~')
        print(missing_products)

products_to_write = []

test_data = {}

with open('./hummingbird_products.json', encoding='utf8') as f:
    print("Loading data from file...")
    test_data = json.load(f)

for product in test_data:
    # BASE PRODUCT
    new_product = {}
    multi_pack = False # pylint: disable=invalid-name

    new_product['Handle'] = product['id']
    new_product['Title'] = product['title']

    description_html = product['description']
    description_soup = BeautifulSoup(description_html, 'html.parser')
    new_product['Body (HTML)'] = ''.join(['<h4>From Hummingbird Wholesale</h4>'] +
        [re.sub('\n', '', str(tag)) for tag in description_soup.find_all(description_filter_text)]
    )

    new_product['Vendor'] = 'Hummingbird Wholesale'
    new_product['Tags'] = ','.join([tag.lower() for tag in product['tags']])
    new_product['Published'] = True

    if len(product['options']) > 1:
        print(
            'NEW OPTION(S) REQUIRED: {0} on {1}//{2}'.format(
                product['options'], new_product['Handle'], new_product['Title']
            )
        )

    primary_variant = product['variants'][0]

    new_product['Option1 Name'] = product['options'][0].capitalize()

    # Check for a multi-pack product
    if re.match(r'.*\d+\s?[x].*', primary_variant['option1']) in const.MULTI_PACK_CONVERTER:
        new_product['Option1 Value'] = const.MULTI_PACK_CONVERTER[primary_variant['option1']]
        multi_pack = True # pylint: disable=invalid-name
    else:
        new_product['Option1 Value'] = primary_variant['option1']

    new_product['Variant SKU'] = primary_variant['sku']

    new_product['Variant Grams'] = 0
    new_product['Variant Inventory Policy'] = 'continue'
    new_product['Variant Fulfillment Service'] = 'manual'
    new_product['Variant Price'] = product['price'] / 100
    new_product['Variant Inventory Tracker'] = 'shopify' if multi_pack else None

    featured_image_src = product['featured_image']
    if featured_image_src.startswith('https:'):
        new_product['Image Src'] = featured_image_src
    else:
        new_product['Image Src'] = 'https:' + featured_image_src

    new_product['Variant Image'] = new_product['Image Src']

    new_product['Image Alt Text'] = new_product['Title']

    new_product['Status'] = 'draft'

    products_to_write.append(new_product)

    # PRODUCT VARIANTS
    for variant in product['variants'][1:]:
        new_variant = {}
        multi_pack = False # pylint: disable=invalid-name

        new_variant['Handle'] = new_product['Handle']

        new_variant['Published'] = True
        new_variant['Option1 Name'] = new_product['Option1 Name']

        # Check for a multi-pack product
        if re.match(r'.*\d+\s?[x].*', variant['option1']) in const.MULTI_PACK_CONVERTER:
            new_variant['Option1 Value'] = const.MULTI_PACK_CONVERTER[variant['option1']]
            multi_pack = True # pylint: disable=invalid-name
        else:
            new_variant['Option1 Value'] = variant['option1']

        new_variant['Variant SKU'] = variant['sku']
        new_variant['Variant Grams'] = 0
        new_variant['Variant Inventory Policy'] = 'continue'
        new_variant['Variant Fulfillment Service'] = 'manual'
        new_variant['Variant Price'] = variant['price'] / 100
        new_variant['Variant Inventory Tracker'] = 'shopify' if multi_pack else None

        if variant['featured_image']:
            new_variant['Variant Image'] = variant['featured_image']['src']

        new_variant['Status'] = 'draft'

        products_to_write.append(new_variant)

with open('products.csv', 'w', encoding='utf8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=const.SHOPIFY_CSV_FIELD_NAMES.values())

    writer.writeheader()

    writer.writerows(products_to_write)
