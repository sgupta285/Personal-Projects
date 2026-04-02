from __future__ import annotations

from functools import lru_cache
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    census_api_key: str | None = Field(default=None, alias="CENSUS_API_KEY")
    census_base_url: str = Field(default="https://api.census.gov/data", alias="CENSUS_BASE_URL")
    default_year: int = Field(default=2022, alias="DEFAULT_YEAR")
    default_dataset: str = Field(default="acs/acs5", alias="DEFAULT_DATASET")

    model_config = SettingsConfigDict(populate_by_name=True, extra="ignore")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()
