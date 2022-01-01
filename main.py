'''
Primary entry point for store scraping code.
'''

import csv
import json
import re
import requests

from bs4 import BeautifulSoup

HUMMINGBIRD_WHOLESALE_BASE_URL: str = 'https://hummingbirdwholesale.com'
PRODUCT_PAGE_SEARCH_SIZE: int = 25
ALL_PRODUCTS_URL: str = '/collections/all'

def paginate(list_to_paginate, page_size=25):
    '''
    Split a list into sub-lists of size = page_size
    '''
    return [
        list_to_paginate[index:index + page_size]
        for index in range(0, len(list_to_paginate), page_size)
    ]

def all_product_ids(query_url, list_of_product_ids = None):
    '''
    Get all product IDs associated with a query URL.
    '''
    list_of_product_ids = list_of_product_ids or []

    # Get the HTML page content
    page = requests.get(HUMMINGBIRD_WHOLESALE_BASE_URL + query_url)

    # Parse the HTML into a BeautifulSoup object
    soup = BeautifulSoup(page.content, "html.parser")

    # Get all possible products on a page
    found_products = soup.find_all(class_='quick-shop-modal')

    available_products = list()

    # Verify the product isn't sold out (will fail to retrieve with query in next step)
    for product in found_products:
        sold_out = product.find(class_='sold_out').text
        if not sold_out:
            available_products.append(product)

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
    paginated_ids = paginate(searchable_ids, PRODUCT_PAGE_SEARCH_SIZE)

    product_data = list()
    missing_products = list()
    # Get product data for each page grouping and add to products list
    for page_number, page in enumerate(paginated_ids):
        print(f'Page number {page_number} of {len(paginated_ids)}')
        response = requests.post(
            f'{HUMMINGBIRD_WHOLESALE_BASE_URL}/search',
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

with open('./hummingbird_products.json', 'w') as jsonfile:
    print('Retrieving product data...')
    product_data, missing_products = all_product_data(all_product_ids(ALL_PRODUCTS_URL))
    print('Saving all products to file...')
    json.dump(product_data, jsonfile)
    print('Products saved to file...')
    if missing_products:
        print('~~~Some Product IDs are Missing From Product Data!!~~~')
        print(missing_products)


####################################################################################
# NEXT: PARSE THE RETURNED JSON INTO CSV AND SAVE TO FILE
# BONUS: FIGURE OUT IF SHOPIFY ALLOWS YOU TO POST A CSV FILE DIRECTLY TO YOUR STORE
####################################################################################
def description_filter_text(tag):
    '''
    Used to filter retrieved description HTML data to usable parts.
    '''
    if tag.name == 'p':
        if not tag.text.strip():
            # Do not include empty <p> tags
            return False
        if tag.parent.name not in ['td']:
            # Don't duplicate tags from tables
            include = True
            for child in tag.children:
                # Don't include <p> tags with <img> objects in them
                if child.name == 'img':
                    include = False

            return include

    if tag.name in ['ul', 'ol', 'table']:
        # Generally include all <ul>, <ol>, and <table> tags (and their children)
        return True

    return False

field_names = {
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

multi_pack_converter = {
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

products_to_write = list()

test_data = dict()

with open('./hummingbird_products.json') as f:
    print("Loading data from file...")
    test_data = json.load(f)

for product in test_data:
    # BASE PRODUCT
    new_product = dict()
    multi_pack = False

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
    if re.match(r'.*\d+\s?[x].*', primary_variant['option1']) in multi_pack_converter.keys():
        new_product['Option1 Value'] = multi_pack_converter[primary_variant['option1']]
        multi_pack = True
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
        new_variant = dict()
        multi_pack = False

        new_variant['Handle'] = new_product['Handle']

        new_variant['Published'] = True
        new_variant['Option1 Name'] = new_product['Option1 Name']

        # Check for a multi-pack product
        if re.match(r'.*\d+\s?[x].*', variant['option1']) in multi_pack_converter.keys():
            new_variant['Option1 Value'] = multi_pack_converter[variant['option1']]
            multi_pack = True
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

with open('products.csv', 'w') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=field_names.values())

    writer.writeheader()

    writer.writerows(products_to_write)
