'''
Unit testing the src/utils.py file
'''

import os
import unittest

from src.utils import format_image_src, paginate, description_filter_text

LOCAL_TEST_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    '..',
    'test_data'
)

class TestFormatImageSrc(unittest.TestCase):
    def test_adds_https_if_needed(self):
        '''
        Adds the https: prefix if it's not there
        '''
        src = '//cdn.shopify.com/s/files/1/0014/7125/0476/products/g100-amaranth.png?v=1533145902'
        formatted_src = format_image_src(src)
        self.assertEqual(formatted_src, 'https:' + src)

    def test_does_not_add_https_if_not_needed(self):
        '''
        Doesn't add the https: prefix if it's already there
        '''
        src = 'https://cdn.shopify.com/s/files/1/0014/7125/0476/products/g100-amaranth.png?v=1533145902'
        formatted_src = format_image_src(src)
        self.assertEqual(formatted_src, src)

class TestPaginate(unittest.TestCase):
    def test_splits_list_into_default_size(self):
        data = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        ]
        self.assertEqual(len(data), 50)
        paginated_data = paginate(data)
        self.assertEqual(len(paginated_data), 2)

        self.assertEqual(len(paginated_data[0]), 25)
        self.assertEqual(len(paginated_data[1]), 25)

    def test_splits_list_into_defined_size(self):
        data = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10
        ]
        self.assertEqual(len(data), 50)
        paginated_data = paginate(data, 10)
        self.assertEqual(len(paginated_data), 5)

        self.assertEqual(len(paginated_data[0]), 10)
        self.assertEqual(len(paginated_data[1]), 10)
        self.assertEqual(len(paginated_data[2]), 10)
        self.assertEqual(len(paginated_data[3]), 10)
        self.assertEqual(len(paginated_data[4]), 10)

    def test_leaves_remainder_in_final_list(self):
        data = [
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5, 6, 7, 8, 9, 10,
            1, 2, 3, 4, 5
        ]
        self.assertEqual(len(data), 45)
        paginated_data = paginate(data, 25)
        self.assertEqual(len(paginated_data), 2)

        self.assertEqual(len(paginated_data[0]), 25)
        self.assertEqual(len(paginated_data[1]), 20)

class TestDescriptionFilterText(unittest.TestCase):
    def setUp(self) -> None:
        import json
        from bs4 import BeautifulSoup

        self.soup_p_and_table = None
        self.soup_p_plus = None
        with open(os.path.join(LOCAL_TEST_DATA_PATH, 'test_data.json')) as jsonfile:
            data = json.load(jsonfile)
            # Amaranth
            description_p_and_table = data[0]['description']
            # Dark Chocolate Covered Hazelnuts
            description_p_plus = data[2]['description']
            self.soup_p_and_table = BeautifulSoup(description_p_and_table, 'html.parser')
            self.soup_p_plus = BeautifulSoup(description_p_plus, 'html.parser')
    
    def test_filter_includes_p_tags(self):
        all_p_tags = self.soup_p_and_table.find_all('p')

        self.assertEqual(len(all_p_tags), 19)

        filtered_p_tags = [p for p in self.soup_p_and_table.find_all(description_filter_text) if p.name == 'p']

        self.assertEqual(len(filtered_p_tags), 7)

        self.assertNotEqual(all_p_tags, filtered_p_tags)

    def test_filter_does_not_include_img_tags(self):
        filtered_tags = self.soup_p_and_table.find_all(description_filter_text)

        image_tags = [tag for tag in filtered_tags if (tag.child and tag.child.name == 'img') or tag.name == 'img']

        self.assertEqual(len(image_tags), 0)

    def test_filter_includes_table_tags(self):
        first_filtered_tags = self.soup_p_and_table.find_all(description_filter_text)
        self.assertEqual(len(first_filtered_tags), 8)

        second_filtered_tags = self.soup_p_plus.find_all(description_filter_text)
        self.assertEqual(len(second_filtered_tags), 3)

        self.assertIn('table', [tag.name for tag in first_filtered_tags])
        self.assertIn('table', [tag.name for tag in second_filtered_tags])

    def test_filter_includes_ul_tags(self):
        first_filtered_tags = self.soup_p_and_table.find_all(description_filter_text)
        self.assertEqual(len(first_filtered_tags), 8)

        second_filtered_tags = self.soup_p_plus.find_all(description_filter_text)
        self.assertEqual(len(second_filtered_tags), 3)

        self.assertNotIn('ul', [tag.name for tag in first_filtered_tags])
        self.assertIn('ul', [tag.name for tag in second_filtered_tags])

    def test_filter_does_not_include_duplicate_tags(self):
        first_filtered_tags = self.soup_p_and_table.find_all(description_filter_text)
        self.assertEqual(len(first_filtered_tags), 8)

        second_filtered_tags = self.soup_p_plus.find_all(description_filter_text)
        self.assertEqual(len(second_filtered_tags), 3)

        self.assertEqual(len(set(first_filtered_tags)), len(first_filtered_tags))
        self.assertEqual(len(set(second_filtered_tags)), len(second_filtered_tags))


if __name__ == '__main__':
    unittest.main()