'''
Testing the hummingbird.get_data code
'''

import json
import os
import re
import unittest
from unittest import mock
from requests import HTTPError
from requests.compat import urlparse

from src.hummingbird.get_data import HummingbirdException, all_product_data, all_product_ids
from src.hummingbird.constants import HUMMINGBIRD_ALL_PRODUCTS_URL, HUMMINGBIRD_WHOLESALE_BASE_URL

LOCAL_TEST_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    'test_data'
)

def mocked_html_data(filename):
    with open(os.path.join(LOCAL_TEST_DATA_PATH, filename)) as htmlfile:
        return htmlfile.read()

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, data, status_code):
            self.status_code = status_code
            self.content = data
        
    if args[0] == HUMMINGBIRD_WHOLESALE_BASE_URL + HUMMINGBIRD_ALL_PRODUCTS_URL:
        return MockResponse(mocked_html_data('id_test_1.html'), 200)

    if args[0] == HUMMINGBIRD_WHOLESALE_BASE_URL + '/collections/all?page=4':
        return MockResponse(mocked_html_data('id_test_2.html'), 200)

    return MockResponse(None, 404)

# This method will be used by the mock to replace requests.post
def mocked_requests_post(*args, **kwargs):
    request_data = kwargs['data']
    request_url = f"{args[0]}?{request_data}"

    class MockResponse:
        def __init__(self, data, status_code):
            self.status_code = status_code
            self.data = data
            self.ok = True if status_code < 400 else False
        
        def json(self):
            return self.data
        
        def raise_for_status(self):
            raise HTTPError()
        
    if request_url.startswith(HUMMINGBIRD_WHOLESALE_BASE_URL + '/search'):
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json')) as jsonfile:
            data = json.load(jsonfile)
            query_ids = re.findall(r'(\d+)', urlparse(request_url).query)
            response_data = []

            for id in query_ids:
                for product in data:
                    if str(product['id']) == str(id):
                        response_data.append(product)

            return MockResponse(response_data, 200)
    
    if len(re.findall(r'(\d+)', urlparse(request_url).query)) < 1:
        return MockResponse(None, 400)

    return MockResponse(None, 404)

# Our test case class
class TestAllProductIds(unittest.TestCase):
    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('src.hummingbird.get_data.requests.get', side_effect=mocked_requests_get)
    def test_get_all_product_ids(self, mock_get):
        list_of_product_ids = [
            '1089424556076', '1089410727980', '1089409286188', '1089420722220', '1089410859052',
            '4383163875376', '4703746588720', '1089415872556', '1089419706412', '1089410990124',
            '1089409843244', '1089411809324', '1089420263468', '1089419640876', '1089416953900',
            '1089420591148', '1089421115436', '1089423835180', '1089419378732', '1089419313196',
            '1089415839788', '1089412300844', '1089416888364', '1089409613868', '1089415282732',
            '4380741206064', '1089413283884', '4738898395184', '1089413906476', '1089415315500',
            '1089417281580', '1089420525612', '1089417314348', '1089417347116', '1089416691756',
            '1089423573036', '1089430814764', '1089430487084', '1089420558380', '4638542954544',
            '1089417379884', '1089427800108', '1089417740332', '1269971779628', '1089424556076',
            '1089410727980', '1089409286188', '1089420722220', '1089410859052', '4383163875376',
            '4703746588720', '1089415872556', '1089419706412', '1089410990124', '1089409843244',
            '1089411809324', '1089420263468', '1089419640876', '1089416953900', '1089420591148',
            '1089421115436', '1089423835180', '1089419378732', '1089419313196', '1089415839788',
            '1089412300844', '1089416888364', '1089409613868', '1089415282732', '4380741206064',
            '1089413283884', '4738898395184', '1089413906476', '1089415315500', '1089417281580',
            '1089420525612', '1089417314348', '1089417347116', '1089416691756', '1089423573036',
            '1089430814764', '1089430487084', '1089420558380', '4638542954544', '1089417379884',
            '1089427800108', '1089417740332', '1269971779628'
        ]

        # Assert products properly parsed + returned
        found_list_of_product_ids = all_product_ids(HUMMINGBIRD_ALL_PRODUCTS_URL)
        self.assertEqual(found_list_of_product_ids, list_of_product_ids)

        # Assert requests.get called with right URL
        self.assertIn(mock.call(HUMMINGBIRD_WHOLESALE_BASE_URL + HUMMINGBIRD_ALL_PRODUCTS_URL), mock_get.call_args_list)
        self.assertIn(mock.call(HUMMINGBIRD_WHOLESALE_BASE_URL + '/collections/all?page=4'), mock_get.call_args_list)

        # Assert requests.get called twice
        self.assertEqual(len(mock_get.call_args_list), 2)

    @mock.patch('src.hummingbird.get_data.requests.get', side_effect=mocked_requests_get)
    def test_get_last_page_of_product_ids(self, mock_get):
        list_of_product_ids = [
            '1089424556076', '1089410727980', '1089409286188',
            '1089420722220', '1089410859052', '4383163875376',
            '4703746588720', '1089415872556', '1089419706412',
            '1089410990124', '1089409843244', '1089411809324',
            '1089420263468', '1089419640876', '1089416953900',
            '1089420591148', '1089421115436', '1089423835180',
            '1089419378732', '1089419313196', '1089415839788',
            '1089412300844', '1089416888364', '1089409613868',
            '1089415282732', '4380741206064', '1089413283884',
            '4738898395184', '1089413906476', '1089415315500',
            '1089417281580', '1089420525612', '1089417314348',
            '1089417347116', '1089416691756', '1089423573036',
            '1089430814764', '1089430487084', '1089420558380',
            '4638542954544', '1089417379884', '1089427800108',
            '1089417740332', '1269971779628'
        ]

        # Assert products properly parsed + returned without a next_page
        found_list_of_product_ids = all_product_ids('/collections/all?page=4')
        self.assertEqual(found_list_of_product_ids, list_of_product_ids)

        # Assert requests.get called with right URL
        self.assertIn(mock.call(HUMMINGBIRD_WHOLESALE_BASE_URL + '/collections/all?page=4'), mock_get.call_args_list)

        # Assert requests.get called once (no next on page)
        self.assertEqual(len(mock_get.call_args_list), 1)

class TestAllProductData(unittest.TestCase):
    # We patch 'requests.post' with our own method. The mock object is passed in to our test case method.
    @mock.patch('src.hummingbird.get_data.requests.post', side_effect=mocked_requests_post)
    def test_get_all_product_data(self, mock_post):
        returned_data, _ = all_product_data(['1089411285036'])
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json')) as jsonfile:
            data = json.load(jsonfile)
            self.assertEqual(returned_data, [data[0]])

    @mock.patch('src.hummingbird.get_data.requests.post', side_effect=mocked_requests_post)
    def test_improper_query_errors(self, mock_post):
        self.assertRaises(HummingbirdException, all_product_data, [])

if __name__ == '__main__':
    unittest.main()