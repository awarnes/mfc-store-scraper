'''
Primary entry point for store scraping code.
'''

import csv
import json
import os

from src.constants import SHOPIFY_CSV_FIELD_NAMES
from src.hummingbird.constants import (
    HUMMINGBIRD_ALL_PRODUCTS_URL,
    HUMMINGBIRD_DATA_FILE,
    HUMMINGBIRD_CSV_FILE)
from src.hummingbird.get_data import all_product_ids, all_product_data
from src.hummingbird.format_data import format_products

LOCAL_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    'outputs'
)

def collect_data(save_to_file=True):
    '''
    Collect data from site, write to file if save_to_file == True
    '''
    raw_data, missing_products = all_product_data(all_product_ids(HUMMINGBIRD_ALL_PRODUCTS_URL))

    if missing_products:
        print('~~~Some Product IDs are Missing From Product Data!!~~~')
        print(missing_products)

    if save_to_file:
        with open(
            os.path.join(LOCAL_DATA_PATH, HUMMINGBIRD_DATA_FILE),
            'w',
            encoding='utf8'
        ) as jsonfile:
            json.dump(raw_data, jsonfile)

    return raw_data, missing_products


def format_data(raw_data, from_file_path=None):
    '''
    Formats collected data and saves as CSV for Shopify import.
    Optionally, can import data from file instead of object
    '''
    if from_file_path:
        raw_data = []
        with open(os.path.join(LOCAL_DATA_PATH, from_file_path), encoding='utf8') as data_file:
            print(f'Loading data from file {from_file_path}...')
            raw_data = json.load(data_file)

    products_to_write = format_products(raw_data)

    with open(os.path.join(LOCAL_DATA_PATH, HUMMINGBIRD_CSV_FILE), 'w', encoding='utf8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=SHOPIFY_CSV_FIELD_NAMES.values())

        writer.writeheader()

        writer.writerows(products_to_write)

if __name__ == '__main__':
    product_data, _ = collect_data(save_to_file=True)

    format_data(product_data)
