from pathlib import Path

import requests

from src.settings import settings


class Shopify:
    _graphql_url = (
        "https://montavillafoodcoop.myshopify.com/admin/api/2026-01/graphql.json"
    )
    _auth_url = "https://montavillafoodcoop.myshopify.com/admin/oauth/access_token"

    access_token: str = None

    def get_token(self):
        resp = requests.post(
            self._auth_url,
            headers={"content-type": "application/json"},
            json={
                "grant_type": "client_credentials",
                "client_id": settings.shopify_client_id,
                "client_secret": settings.shopify_client_secret,
            },
            timeout=5,
        )

        access_token = resp.json().get("access_token")

        self.access_token = access_token

        return self.access_token

    def query(self, query: str):
        if not self.access_token:
            self.get_token()

        resp = requests.post(
            self._graphql_url,
            headers={
                "content-type": "application/json",
                "x-shopify-access-token": self.access_token,
            },
            json={"query": query},
            timeout=5,
        )

        if resp.ok:
            return resp.json()

    def query_file(self, path: str):
        query = Path(path).read_text()

        if not self.access_token:
            self.get_token()

        resp = requests.post(
            self._graphql_url,
            headers={
                "content-type": "application/json",
                "x-shopify-access-token": self.access_token,
            },
            json={"query": query},
            timeout=5,
        )

        if resp.ok:
            return resp.json()


if __name__ == "__main__":
    s = Shopify()
    print(s.query_file("./src/shopify/queries/get_products.graphql"))
