# from src.hummingbird.format_data import is_multi_pack, get_multi_pack_amount, get_product_price
# import json

# with open('./outputs/hummingbird_products.json') as file:
#     data = json.load(file)

#     for product in data:
#         if product['id'] == 4383082479664:
#             print(json.dumps(product))

from src.shopify.shopify import Shopify

if __name__ == "__main__":
    s = Shopify()
    print(s.query_file("./src/shopify/queries/get_products.graphql"))
