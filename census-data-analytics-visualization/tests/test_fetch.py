from censusviz.config import Settings
from censusviz.fetch import CensusAPIClient


def test_build_url_uses_dataset_and_year():
    client = CensusAPIClient(Settings(CENSUS_BASE_URL="https://api.census.gov/data", DEFAULT_YEAR=2021, DEFAULT_DATASET="acs/acs5"))
    assert client.build_url(2021, "acs/acs5") == "https://api.census.gov/data/2021/acs/acs5"
