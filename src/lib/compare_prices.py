'''
Used to compare archived prices to newly pulled prices and alert on which products have updated prices.

e.g. python compare_prices.py ../../outputs/archive/hummingbird_products_20220228.csv ../../outputs/archive/hummingbird_products_20220410.csv
'''

import argparse
import csv, json
from collections import defaultdict

parser = argparse.ArgumentParser(description='Compare prices between CSV files and display the differences.')
parser.add_argument('-o', '--old', help='Path to the older prices in CSV format.')
parser.add_argument('-n', '--new', help='Path to the newer prices in CSV format.')

args = parser.parse_args()

old_path = args.old
new_path = args.new
{
    'Handle': '1089409187884',
    'Title': '',
    'Tags': '',
    'Option1 Name': 'Size',
    'Option1 Value': '5 lb bag',
    'Variant Price': '36.25'
}
def default_value():
    return {'variants': [], 'title': ''}

def get_csv_data(file_path):
    '''
    Returns obects with the following format:
    {
        "4738898395184": {
            "variants": [
            {
                "tags": "nuts",
                "option_name": "Size",
                "option_value": "25 lb box",
                "price": "350.5"
            },
            {
                "tags": "",
                "option_name": "Size",
                "option_value": "5 lb bag",
                "price": "77.25"
            }
            ],
            "title": "Hazelnuts, Whole, Raw, Unpasteurized"
        }
    }
    '''
    data = defaultdict(default_value)
    with open(file_path) as csvfile:
        csvreader = csv.DictReader(csvfile)
        for row in csvreader:
            variant = {
                'tags': row['Tags'],
                'size': row['Option1 Value'],
                'price': row['Variant Price'],
            }
            if len(data[row['Handle']]['title']) < 1:
                data[row['Handle']]['title'] = row['Title']
            data[row['Handle']]['variants'].append(variant)

    return data


old_data = get_csv_data(old_path)
new_data = get_csv_data(new_path)

changed_products = []
for key in old_data.keys():
    old_product = old_data[key]
    new_product = new_data[key]

    for old_variant in old_product['variants']:
        for new_variant in new_product['variants']:
            if old_variant['size'] == new_variant['size'] and \
                old_variant['price'] != new_variant['price']:
                changed_products.append({
                    'handle': key,
                    'title': new_product['title'],
                    'size': new_variant['size'],
                    'new_price': new_variant['price'],
                    'old_price': old_variant['price']
                })

print(f'Found {len(changed_products)} updated prices...')
print(json.dumps(changed_products))
