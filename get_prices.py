"""
This file gets the prices from the new Hummingbird Wholesale forms
and writes them to a CSV. This can then be used to manually update prices in Shopify
Add the output data to this sheet with the date for archiving:
https://docs.google.com/spreadsheets/d/1yt8LAMR7M6Hc00Zvtrptw867q7Dsp9LSVdVxcQMvjmM/edit#gid=0

You'll need to login to the Hummingbird wholesale website and get the _secure_session_id token
from the cookies and update it on line 119 of the src/hummingbird/get_data.py file.
"""

import csv, math

from src.hummingbird.get_data import all_wof_collection_data

data = all_wof_collection_data()

csv_data = []
for product in data:
    try:
        for variant in product['productVariants']:
            row = []
            # row.append(product['productId'])
            row.append(product['productTitle'])
            row.append(variant['variantTitle'])
            raw_price = int(variant['variantRawPrice'])
            sell_price = math.ceil(raw_price * 1.3)
            row.append((sell_price - ((sell_price % 25) - 25)) / 100)
            row.append(raw_price / 100)

            csv_data.append(row)
    except KeyError as err:
        pass


with open('data.csv', 'w') as f:
    writer = csv.writer(f)
    writer.writerow(['Product Name', 'Variant', 'Sell Price', 'Purchase Price'])
    for d in csv_data:
        writer.writerow(d)