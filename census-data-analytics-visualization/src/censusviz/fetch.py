from __future__ import annotations

from dataclasses import dataclass
from typing import Any
import requests

from .config import Settings


@dataclass(slots=True)
class CensusAPIClient:
    settings: Settings

    def build_url(self, year: int, dataset: str) -> str:
        return f"{self.settings.census_base_url.rstrip('/')}/{year}/{dataset}"

    def fetch(self, variables: list[str], geography: str, for_clause: str, in_clause: str | None = None) -> list[list[Any]]:
        params = {"get": ",".join(variables), "for": for_clause}
        if in_clause:
            params["in"] = in_clause
        if self.settings.census_api_key:
            params["key"] = self.settings.census_api_key
        response = requests.get(self.build_url(self.settings.default_year, self.settings.default_dataset), params=params, timeout=30)
        response.raise_for_status()
        return response.json()
