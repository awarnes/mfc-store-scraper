"""Module for managing Shopify GraphQL mutation files"""

import os
from pathlib import Path

class Mutations:
    """Class for managing GraphQL mutation files"""
    _query_directory = os.path.dirname(os.path.abspath(__file__))

    file_create = Path(os.path.join(_query_directory, 'file_create.graphql')).read_text(encoding="utf-8")
    generate_staged_uploads = Path(os.path.join(_query_directory, 'generate_staged_uploads.graphql')).read_text(encoding="utf-8")
    product_create = Path(os.path.join(_query_directory, 'product_create.graphql')).read_text(encoding="utf-8")
    product_update = Path(os.path.join(_query_directory, 'product_update.graphql')).read_text(encoding="utf-8")
    product_variants_bulk_update = Path(os.path.join(_query_directory, 'product_variants_bulk_update.graphql')).read_text(encoding="utf-8")
