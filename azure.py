import json
import logging

import requests

# These two lines enable debugging at httplib level (requests->urllib3->http.client)
# You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# The only thing missing will be the response.body which is not logged.
try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client
http_client.HTTPConnection.debuglevel = 1

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

app_id = "J8N8I8KE2Y"
api_key = "2982ea7ae8fdc7ed1772c496260d35f5"
index_name = "products"

if __name__ == "__main__":
    page = 0
    num_pages = 100000
    hits = []

    while page < num_pages:
        resp = requests.post(
            f"https://{app_id}-dsn.algolia.net/1/indexes/products/query?x-algolia-application-id={app_id}&x-algolia-api-key={api_key}",
            headers={
                "content-type": "application/x-www-form-urlencoded",
                "accept": "application/json",
            },
            json={
                "params": f"query=&filters=packaging.stock%20%3E%200&attributesToHighlight=&attributesToRetrieve=id%2Cbrand.name%2Cname%2Csubstitutions%2Cfavorites%2CstorageClimate%2Cslug%2CisShippableUps%2CmaxStorageDays%2CtreatAsActive%2CunshippableRegions%2Cpackaging.code%2Cpackaging.price%2Cpackaging.weight%2Cpackaging.volume%2Cpackaging.tags%2Cpackaging.images%2Cpackaging.size%2Cpackaging.stock%2Cpackaging.next-purchase-arrival%2Cpackaging.favorites%2Cpackaging.bargain-bin-notes%2Cpackaging.rewardsEnabled%2Cpackaging.trustpilotNumberOfReviews%2Cpackaging.trustpilotStarsAverage%2Cpackaging.freightHandlingRequired%2Cpackaging.vendorShortedLastPurchase%2Cpackaging.primary-category&queryType=prefixNone&facetFilters=%5B%5B%5D%2C%22category-ids%3A21244%22%2C%5B%5D%5D&optionalFilters=%5B%22isPromoted%3Atrue%22%5D&hitsPerPage=500&page={page}"
            },
        )

        hits += resp.json()["hits"]
        num_pages = resp.json()["nbPages"]
        page += 1

    print(json.dumps(hits))
    print(len(hits))
    with open("data.json", "w") as f:
        f.write(json.dumps(hits))
