from src.hummingbird.format_data import is_multi_pack, get_multi_pack_amount, get_product_price
import json, csv, math

# with open('./outputs/hummingbird_products.json') as file:
#     data = json.load(file)

#     for product in data:
#         if product['id'] == 4383082479664:
#             print(json.dumps(product))


from src.hummingbird.get_data import all_wof_collection_data

data = []
with open('./outputs/archive/hummingbird_products_20230323.json', 'r') as jsonfile:
    data = json.load(jsonfile)

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
    for d in csv_data:
        writer.writerow(d)