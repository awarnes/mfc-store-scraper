"""Module for managing Shopify GraphQL connections"""

import requests

from src.settings import settings
from src.shopify.mutations import Mutations
from src.shopify.queries import Queries

class ShopifyQueryError(Exception):
    """Generic error for a failed Shopify query"""


class Shopify:
    """Class for handling Shopify GraphQL queries and mutations"""

    _graphql_url = (
        "https://montavillafoodcoop.myshopify.com/admin/api/2026-01/graphql.json"
    )
    _auth_url = "https://montavillafoodcoop.myshopify.com/admin/oauth/access_token"

    access_token: str | None = None

    def get_token(self):
        """Get bearer token from Shopify"""
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

    def query(self, query: str, variables: dict) -> dict:
        """Perform GraphQL query against Shopify store"""
        if not self.access_token:
            self.get_token()

        resp = requests.post(
            self._graphql_url,
            headers={
                "content-type": "application/json",
                "x-shopify-access-token": self.access_token,
            },
            json={"query": query, "variables": variables},
            timeout=5,
        )

        if resp.ok:
            return resp.json()

        raise ShopifyQueryError()

    def query_file(self, query: Queries | Mutations, variables: dict) -> dict:
        """Perform GraphQL query against Shopify store using given .graphql file"""
        if not self.access_token:
            self.get_token()

        resp = requests.post(
            self._graphql_url,
            headers={
                "content-type": "application/json",
                "x-shopify-access-token": self.access_token,
            },
            json={"query": query, "variables": variables},
            timeout=5,
        )

        if resp.ok:
            return resp.json()

        raise ShopifyQueryError()

    def current_app(self):
        """Returns data on the currently authenticated application"""

        return self.query_file(
            Queries.current_app_installation, {}
        )
