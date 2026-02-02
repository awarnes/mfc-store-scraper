"""Wrapper class for scraping data from the Azure website"""

import json
from typing import Dict, List

import requests

from src.settings import settings

class Azure:
    """Wrapper class for scraping data from Azure website"""
    app_id = ""
    api_key = ""

    def __init__(self, app_id=None, api_key=None):
        self.app_id = app_id or settings.app_id
        self.api_key = api_key or settings.api_key

    def get_url(self, search_index):
        """Get the URL for Azure API access"""
        # pylint: disable=line-too-long
        return f"https://{self.app_id}-dsn.algolia.net/1/indexes/{search_index}/query?x-algolia-application-id={self.app_id}&x-algolia-api-key={self.api_key}"

    def headers(self):
        """Common headers for requests"""
        return {
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

    def get_d1_categories(self):
        """Get depth=1 categories for Azure"""
        resp = requests.post(
            self.get_url("categories"),
            headers=self.headers(),
            json={
                "params": "query=&attributesToHighlight=&filters=depth=1&hitsPerPage=5000"
            },
            timeout=5
        )

        return resp.json().get("hits")

    def get_products_for_category(self, category_id, page=0):
        """Get all products for a given category"""
        # pylint: disable=line-too-long
        resp = requests.post(
            self.get_url("products"),
            headers=self.headers(),
            json={
                "params": f"query=&filters=packaging.stock%20%3E%200&attributesToHighlight=&attributesToRetrieve=id%2Cbrand.name%2Cname%2Csubstitutions%2Cfavorites%2CstorageClimate%2Cslug%2CmaxStorageDays%2CtreatAsActive%2CunshippableRegions%2Cpackaging.code%2Cpackaging.price%2Cpackaging.weight%2Cpackaging.volume%2Cpackaging.tags%2Cpackaging.images%2Cpackaging.size%2Cpackaging.stock%2Cpackaging.next-purchase-arrival%2Cpackaging.favorites%2Cpackaging.bargain-bin-notes%2Cpackaging.rewardsEnabled%2Cpackaging.freightHandlingRequired%2Cpackaging.vendorShortedLastPurchase%2Cpackaging.primary-category%2Cdescription%2CshortDescription&queryType=prefixNone&facetFilters=%5B%5B%5D%2C%22category-ids%3A{category_id}%22%2C%5B%5D%5D&optionalFilters=%5B%22isPromoted%3Atrue%22%5D&hitsPerPage=5000&page={page}"
            },
            timeout=5
        )

        return resp.json()

    def get_all_products(self):
        """Get all Azure products"""
        hits = []
        for category in self.get_d1_categories():
            page = 0
            num_pages = 100000

            while page < num_pages:
                resp = self.get_products_for_category(category.get("id"), page)
                if resp.get("nbHits") >= 2000:
                    print(f"More than 2k products in category: {category['id']}")
                hits += resp.get("hits")
                num_pages = resp.get("nbPages")
                page += 1

        return hits

    def get_local_products(self):
        """Get products from a local file"""
        with open("../../outputs/data.json", "r", encoding='utf8') as f:
            return json.loads(f.read())

    def format_products(self, unformatted_products) -> tuple[List[Dict], List[Dict], List[Dict]]:
        """Format Azure products for insertion into database"""
        products = []
        packaging = []
        prices = []

        for product in unformatted_products:
            products.append(
                {
                    "id": product.get("id"),
                    "name": product.get("name"),
                    "short_description": product.get("shortDescription"),
                    "description": product.get("description"),
                    "slug": product.get("slug"),
                    "storage_climate": product.get("storageClimate"),
                    "unshippable_regions": json.dumps(
                        product.get("unshippableRegions")
                    ),
                    "brand": json.dumps(product.get("brand")),
                    "substitutions": json.dumps(product.get("substitutions")),
                }
            )

            for pack in product.get("packaging"):
                packaging.append(
                    {
                        "products_id": product.get("id"),
                        "code": pack.get("code"),
                        "size": pack.get("size"),
                        "weight": json.dumps(pack.get("weight")),
                        "stock": pack.get("stock"),
                        "images": json.dumps(pack.get("images")),
                        "rewards_enabled": pack.get("rewardsEnabled"),
                        "freight_handling_required": pack.get(
                            "freightHandlingRequired"
                        ),
                        "tags": json.dumps(pack.get("tags")),
                        "primary_category": pack.get("primary-category"),
                        "favorites": pack.get("favorites"),
                        "next_purchase_arrival": pack.get("next-purchase-arrival"),
                    }
                )

                prices.append(
                    {
                        "packaging_code": pack.get("code"),
                        "retail_dollars": pack.get("price")
                        .get("retail", {})
                        .get("dollars"),
                        "retail_unit": pack.get("price").get("retail", {}).get("unit"),
                        "wholesale_dollars": pack.get("price")
                        .get("wholesale", {})
                        .get("dollars"),
                        "wholesale_unit": pack.get("price")
                        .get("wholesale", {})
                        .get("unit"),
                    }
                )

        return (products, packaging, prices)
