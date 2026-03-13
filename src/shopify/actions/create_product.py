"""Module for creating products in Shopify and saving data in the database"""

from src.shopify.shopify import Shopify


def create_product(product):
    """Function for creating a product, adding media, and updating variants"""
