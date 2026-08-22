"""Module for managing Shopify GraphQL connections"""

import random
import time

import requests

from src.lib.logger import logger
from src.settings import settings
from src.shopify.mutations import Mutations
from src.shopify.queries import Queries


class ShopifyQueryError(Exception):
    """Generic error for a failed Shopify query"""


class ShopifyThrottledError(ShopifyQueryError):
    """Raised when Shopify keeps throttling us past MAX_RETRIES."""


class ShopifyConnectionError(ShopifyQueryError):
    """Raised when we can't reach or authenticate to the store."""


# Tunables
MAX_RETRIES = 5
MIN_HEADROOM_MULTIPLIER = 4
MIN_HEADROOM_ABSOLUTE = 100

API_VERSION = "2026-01"


class Shopify:
    """Client for a single Shopify store's Admin GraphQL API.

    Store domain and credentials are read from settings. Only one store
    is supported per session.
    """

    access_token: str | None = None

    def __init__(
        self,
        shop_domain: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
        api_version: str = API_VERSION,
    ):
        self.shop_domain = shop_domain or settings.shopify_shop_domain
        self.client_id = client_id or settings.shopify_client_id
        self.client_secret = client_secret or settings.shopify_client_secret
        self.api_version = api_version

    @property
    def graphql_url(self) -> str:
        return f"https://{self.shop_domain}/admin/api/{self.api_version}/graphql.json"

    @property
    def auth_url(self) -> str:
        return f"https://{self.shop_domain}/admin/oauth/access_token"

    def get_token(self) -> str:
        """Get bearer token from Shopify"""
        try:
            resp = requests.post(
                self.auth_url,
                headers={"content-type": "application/json"},
                json={
                    "grant_type": "client_credentials",
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                },
                timeout=5,
            )
        except requests.RequestException as e:
            raise ShopifyConnectionError(
                f"Could not reach {self.shop_domain}: {e}"
            ) from e

        if not resp.ok:
            raise ShopifyConnectionError(
                f"Auth failed for {self.shop_domain}: "
                f"HTTP {resp.status_code} {resp.text[:200]}"
            )

        access_token = resp.json().get("access_token")
        if not access_token:
            raise ShopifyConnectionError(
                f"No access_token in auth response from {self.shop_domain}"
            )

        self.access_token = access_token
        return self.access_token

    def check_connection(self) -> dict:
        """Verify credentials and reachability. Returns basic app info."""
        try:
            self.get_token()
            resp = self.current_app()
        except ShopifyConnectionError:
            raise
        except Exception as e:
            raise ShopifyConnectionError(
                f"Connection check failed for {self.shop_domain}: {e}"
            ) from e

        if resp.get("errors"):
            raise ShopifyConnectionError(
                f"Connection check errors: {resp['errors']}"
            )

        logger.info(f"Connected to {self.shop_domain}")
        return resp.get("data", {})

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    @staticmethod
    def _is_throttled(payload: dict) -> bool:
        for err in payload.get("errors", []) or []:
            if (err.get("extensions") or {}).get("code") == "THROTTLED":
                return True
        return False

    @staticmethod
    def _throttle_status(payload: dict) -> dict | None:
        cost = (payload.get("extensions") or {}).get("cost") or {}
        return cost.get("throttleStatus")

    @staticmethod
    def _actual_cost(payload: dict) -> float:
        cost = (payload.get("extensions") or {}).get("cost") or {}
        return float(cost.get("actualQueryCost") or cost.get("requestedQueryCost") or 0)

    @classmethod
    def _sleep_to_refill(cls, throttle: dict, target: float) -> None:
        available = float(throttle.get("currentlyAvailable", 0))
        restore = float(throttle.get("restoreRate", 0)) or 1.0
        if available >= target:
            return
        deficit = target - available
        seconds = deficit / restore
        logger.debug(
            f"Shopify bucket low ({available:.0f}/{throttle.get('maximumAvailable')}); "
            f"sleeping {seconds:.2f}s to refill to {target:.0f}"
        )
        time.sleep(seconds)

    def _execute(self, query: str, variables: dict) -> dict:
        """Send a GraphQL request with throttle-aware retries and pacing."""
        if not self.access_token:
            self.get_token()

        for attempt in range(1, MAX_RETRIES + 1):
            resp = requests.post(
                self.graphql_url,
                headers={
                    "content-type": "application/json",
                    "x-shopify-access-token": self.access_token,
                },
                json={"query": query, "variables": variables},
                timeout=30,
            )

            if not resp.ok:
                raise ShopifyQueryError(
                    f"HTTP {resp.status_code}: {resp.text[:500]}"
                )

            payload = resp.json()

            if self._is_throttled(payload):
                throttle = self._throttle_status(payload) or {}
                target = max(
                    MIN_HEADROOM_ABSOLUTE,
                    float(throttle.get("maximumAvailable", 1000)) / 2,
                )
                self._sleep_to_refill(throttle, target)
                time.sleep(random.uniform(0.1, 0.5) * attempt)
                logger.warning(
                    f"Shopify throttled (attempt {attempt}/{MAX_RETRIES}); retrying"
                )
                continue

            throttle = self._throttle_status(payload)
            if throttle:
                last_cost = self._actual_cost(payload)
                headroom = max(
                    MIN_HEADROOM_ABSOLUTE,
                    last_cost * MIN_HEADROOM_MULTIPLIER,
                )
                self._sleep_to_refill(throttle, headroom)

            return payload

        raise ShopifyThrottledError(
            f"Still throttled after {MAX_RETRIES} attempts"
        )

    # ------------------------------------------------------------------ #
    # Public API
    # ------------------------------------------------------------------ #

    def query(self, query: str, variables: dict) -> dict:
        """Perform GraphQL query against Shopify store"""
        return self._execute(query, variables)

    def query_file(self, query: Queries | Mutations, variables: dict) -> dict:
        """Perform GraphQL query against Shopify store using a .graphql file"""
        return self._execute(query, variables)

    def current_app(self):
        """Returns data on the currently authenticated application"""
        return self.query_file(Queries.current_app_installation, {})
