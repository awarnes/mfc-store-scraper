"""
Getting data from the Hummingbird Wholesale site
"""

import re

from bs4 import BeautifulSoup
import requests

from src.constants import PRODUCT_PAGE_SEARCH_SIZE
from src.utils import paginate
from src.hummingbird.constants import HUMMINGBIRD_WHOLESALE_BASE_URL

class HummingbirdException(Exception):
    '''Exception for Hummingbird calls'''
    def __init__(self, value):
        self.value = value
        super().__init__()

    def __str__(self):
        return repr(self.value)

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
    if len(searchable_ids) < 1:
        raise HummingbirdException("There are no id's to search!")
    print(f"Retrieving data for {len(searchable_ids)} total products...")

    # Paginate IDs into 'reasonable' chunks ¯\_(ツ)_/¯
    paginated_ids = paginate(searchable_ids, PRODUCT_PAGE_SEARCH_SIZE)

    product_data = [] # pylint: disable=redefined-outer-name
    missing_products = [] # pylint: disable=redefined-outer-name
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
