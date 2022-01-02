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

def all_product_ids(query_url, list_of_product_ids = None):
    '''
    Get all product IDs associated with a query URL.
    '''
    list_of_product_ids = list_of_product_ids or []

    # Get the HTML page content
    page = requests.get(const.HUMMINGBIRD_WHOLESALE_BASE_URL + query_url)

    # Parse the HTML into a BeautifulSoup object
    soup = BeautifulSoup(page.content, "html.parser")

    # Get all possible products on a page
    found_products = soup.find_all(class_='quick-shop-modal')

    available_products = []

    # Verify the product isn't sold out (will fail to retrieve with query in next step)
    for found_product in found_products:
        sold_out = found_product.find(class_='sold_out').text
        if not sold_out:
            available_products.append(found_product)

    # Collect the list of all product IDs on the page and format them 'properly'
    list_of_product_ids += [
        re.sub('product-', '', product.attrs['id'])
        for product in available_products
    ]

    # Check for another page
    next_page = soup.find(class_='next')

    # If there's another page go there
    if next_page:
        next_page = next_page.next.attrs['href']
        return all_product_ids(next_page, list_of_product_ids)

    # Otherwise return the list of IDs
    return list_of_product_ids

def all_product_data(ids_to_search):
    '''
    Get all product data given a list of IDs to search
    '''
    # Get unique IDs and format IDs to search
    searchable_ids = [f'id:{id}' for id in set(ids_to_search)]

    print(f"Retrieving data for {len(searchable_ids)} total products...")

    # Paginate IDs into 'reasonable' chunks ¯\_(ツ)_/¯
    paginated_ids = utils.paginate(searchable_ids, const.PRODUCT_PAGE_SEARCH_SIZE)

    product_data = [] # pylint: disable=redefined-outer-name
    missing_products = [] # pylint: disable=redefined-outer-name
    # Get product data for each page grouping and add to products list
    for page_number, page in enumerate(paginated_ids):
        print(f'Page number {page_number} of {len(paginated_ids)}')
        response = requests.post(
            f'{const.HUMMINGBIRD_WHOLESALE_BASE_URL}/search',
            data=f'q={" OR ".join(page)}&view=globo.alsobought'
        )
        if response.ok:
            response_json = response.json()
            print(f'returned data for {len(response_json)} of {len(page)} products queried')
            product_data += response_json
            if len(response_json) != len(page):
                missing_products += [
                    product_id for product_id in page
                    if re.sub('id:', '', product_id) not in [
                        str(product['id']) for product in response_json
                    ]
                ]
        else:
            response.raise_for_status()

    if missing_products:
        missing_products = [re.sub('id:', '', product_id) for product_id in missing_products]

    return product_data, missing_products

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
