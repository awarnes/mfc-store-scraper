import json

import requests

from constants import API_KEY, APP_ID


class Azure:
    app_id = ""
    api_key = ""

    def __init__(self, app_id=APP_ID, api_key=API_KEY):
        self.app_id = app_id
        self.api_key = api_key

    def get_url(self, search_index):
        return f"https://{self.app_id}-dsn.algolia.net/1/indexes/{search_index}/query?x-algolia-application-id={self.app_id}&x-algolia-api-key={self.api_key}"

    def headers(self):
        return {
            "content-type": "application/x-www-form-urlencoded",
            "accept": "application/json",
        }

    def get_d1_categories(self):
        resp = requests.post(
            self.get_url("categories"),
            headers=self.headers(),
            json={
                "params": "query=&attributesToHighlight=&filters=depth=1&hitsPerPage=5000"
            },
        )

        return resp.json()["hits"]

    def get_products_for_category(self, category_id, page=0):
        resp = requests.post(
            self.get_url("products"),
            headers=self.headers(),
            json={
                "params": f"query=&filters=packaging.stock%20%3E%200&attributesToHighlight=&attributesToRetrieve=id%2Cbrand.name%2Cname%2Csubstitutions%2Cfavorites%2CstorageClimate%2Cslug%2CmaxStorageDays%2CtreatAsActive%2CunshippableRegions%2Cpackaging.code%2Cpackaging.price%2Cpackaging.weight%2Cpackaging.volume%2Cpackaging.tags%2Cpackaging.images%2Cpackaging.size%2Cpackaging.stock%2Cpackaging.next-purchase-arrival%2Cpackaging.favorites%2Cpackaging.bargain-bin-notes%2Cpackaging.rewardsEnabled%2Cpackaging.freightHandlingRequired%2Cpackaging.vendorShortedLastPurchase%2Cpackaging.primary-category%2Cdescription%2CshortDescription&queryType=prefixNone&facetFilters=%5B%5B%5D%2C%22category-ids%3A{category_id}%22%2C%5B%5D%5D&optionalFilters=%5B%22isPromoted%3Atrue%22%5D&hitsPerPage=5000&page={page}"
            },
        )

        return resp.json()

    def get_all_products(self):
        hits = []
        for category in self.get_d1_categories():
            page = 0
            num_pages = 100000

            while page < num_pages:
                resp = self.get_products_for_category(category["id"], page)
                if resp["nbHits"] >= 2000:
                    print(f"More than 2k products in category: {category['id']}")
                hits += resp["hits"]
                num_pages = resp["nbPages"]
                page += 1

        return hits


if __name__ == "__main__":
    azure = Azure()

    all_products = azure.get_all_products()

    print(len(all_products))
    with open("data.json", "w") as f:
        f.write(json.dumps(all_products))
