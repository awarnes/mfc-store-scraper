'''
Tests src.hummingbird.format_data functionality
'''
import json
import os
import unittest

from src.hummingbird.format_data import (
    format_products,
    is_multi_pack,
    get_multi_pack_amount,
    get_product_price
)

# pylint: disable=line-too-long,missing-function-docstring,missing-class-docstring

LOCAL_TEST_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    '..',
    'test_data'
)

class TestIsMultiPack(unittest.TestCase):
    def setUp(self) -> None:
        self.data = None

        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json'), encoding='utf8') as jsonfile:
            self.data = json.load(jsonfile)

    def test_returns_true_if_is_multi_pack(self):
        multi_pack_variant = self.data[2]['variants'][0]
        self.assertTrue(is_multi_pack(multi_pack_variant))

    def test_returns_false_if_is_not_multi_pack(self):
        non_multi_pack_variant = self.data[0]['variants'][0]
        self.assertFalse(is_multi_pack(non_multi_pack_variant))

    def test_returns_false_if_product_does_not_contain_option1(self):
        variant_missing_option1 = {
            'test_key': 'apple',
            'test_key_2': 'sauce'
        }

        self.assertFalse(is_multi_pack(variant_missing_option1))

class TestGetMultiPackAmount(unittest.TestCase):
    def setUp(self) -> None:
        self.data = None

        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json'), encoding='utf8') as jsonfile:
            self.data = json.load(jsonfile)

    def test_returns_the_correct_amount(self):
        multi_pack_variant_one = self.data[2]['variants'][0]
        multi_pack_variant_two = self.data[2]['variants'][1]

        self.assertEqual(get_multi_pack_amount(multi_pack_variant_one), 6)
        self.assertEqual(get_multi_pack_amount(multi_pack_variant_two), 8)

    def test_returns_1_if_not_multi_pack(self):
        non_multi_pack_variant = self.data[0]['variants'][0]

        self.assertEqual(get_multi_pack_amount(non_multi_pack_variant), 1)

    def test_returns_1_if_variant_malformed(self):
        non_multi_pack_variant = {
            'apple': 'sauce',
            'gary': 'indiana'
        }

        self.assertEqual(get_multi_pack_amount(non_multi_pack_variant), 1)

class TestGetProductPrice(unittest.TestCase):
    def test_returns_right_value_with_no_multi_pack_amount(self):
        price = 5000
        self.assertEqual(get_product_price(price), 50.0)

    def test_returns_right_value_with_evenly_divisible_dollars_multi_pack_amount(self):
        price = 5000
        multi_pack_amount = 5
        self.assertEqual(get_product_price(price, multi_pack_amount), 10.0)

    def test_returns_right_value_evenly_divisible_cents_multi_pack_amount(self):
        price = 5000
        multi_pack_amount = 4
        self.assertEqual(get_product_price(price, multi_pack_amount), 12.5)

    def test_returns_right_value_with_not_evenly_divisible_multi_pack_amount(self):
        price = 5000
        multi_pack_amount = 6
        self.assertEqual(get_product_price(price, multi_pack_amount), 8.34)

class TestFormatProducts(unittest.TestCase):
    def setUp(self) -> None:
        self.raw_data = None

        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json'), encoding='utf8') as jsonfile:
            self.raw_data = json.load(jsonfile)

    def test_returns_properly_formatted_single_variant_product(self):
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'formatted_single_variant_product.json'), encoding='utf8') as formatted_file:
            formatted_data = json.load(formatted_file)
            self.assertEqual(format_products([self.raw_data[0]]), formatted_data)

    def test_returns_properly_formatted_multi_variant_product(self):
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'formatted_multi_variant_product.json'), encoding='utf8') as formatted_file:
            formatted_data = json.load(formatted_file)
            self.assertEqual(format_products([self.raw_data[1]]), formatted_data)

    def test_returns_properly_formatted_multi_pack_product(self):
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'formatted_multi_pack_product.json'), encoding='utf8') as formatted_file:
            formatted_data = json.load(formatted_file)
            self.assertEqual(format_products([self.raw_data[2]]), formatted_data)

if __name__ == '__main__':
    unittest.main()
