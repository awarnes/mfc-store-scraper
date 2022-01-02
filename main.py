'''
Primary entry point for store scraping code.
'''

import csv
import json

from src.constants import SHOPIFY_CSV_FIELD_NAMES
from src.hummingbird.constants import ALL_PRODUCTS_URL
from src.hummingbird.get_data import all_product_ids, all_product_data
from src.hummingbird.format_data import format_products

with open('./hummingbird_products.json', 'w', encoding='utf8') as jsonfile:
    print('Retrieving product data...')
    product_data, missing_products = all_product_data(all_product_ids(ALL_PRODUCTS_URL))
    print('Saving all products to file...')
    json.dump(product_data, jsonfile)
    print('Products saved to file...')
    if missing_products:
        print('~~~Some Product IDs are Missing From Product Data!!~~~')
        print(missing_products)

product_data = {}

with open('./hummingbird_products.json', encoding='utf8') as f:
    print("Loading data from file...")
    product_data = json.load(f)

products_to_write = format_products(product_data)

with open('products.csv', 'w', encoding='utf8') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=SHOPIFY_CSV_FIELD_NAMES.values())

    writer.writeheader()

    writer.writerows(products_to_write)
