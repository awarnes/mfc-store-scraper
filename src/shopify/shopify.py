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


# Tunables
MAX_RETRIES = 5
# If remaining bucket < MIN_HEADROOM * last_cost, sleep to refill before returning.
MIN_HEADROOM_MULTIPLIER = 4
# Absolute floor to always leave in the bucket.
MIN_HEADROOM_ABSOLUTE = 100


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
        """Sleep just long enough for the bucket to reach `target`."""
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
                self._graphql_url,
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
                # Sleep until the bucket has enough for one query of typical size,
                # plus a small jittered backoff.
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

            # Success — proactively pace if we're running low.
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
