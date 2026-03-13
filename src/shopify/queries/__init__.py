"""Module for managing Shopify GraphQL query files"""

import os
from pathlib import Path

class Queries:
    """Class for managing GraphQL query files"""
    _query_directory = os.path.dirname(os.path.abspath(__file__))

    check_file_status = Path(os.path.join(_query_directory, 'check_file_status.graphql')).read_text(encoding="utf-8")
    current_app_installation = Path(os.path.join(_query_directory, 'current_app_installation.graphql')).read_text(encoding="utf-8")
    get_products = Path(os.path.join(_query_directory, 'get_products.graphql')).read_text(encoding="utf-8")
