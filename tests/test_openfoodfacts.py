"""
tests/test_openfoodfacts.py
----------------------------
Unit tests for app/modules/openfoodfacts.py.

All HTTP calls are mocked with unittest.mock so no real network requests
are made during the test run.
"""
import pytest
from unittest.mock import patch, MagicMock
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from modules.openfoodfacts import fetch_by_barcode, fetch_by_name, barcode_data_cleaner, name_data_cleaner


# ---------------------------------------------------------------------------
# Shared mock helpers
# ---------------------------------------------------------------------------
def _mock_response(status_code=200, json_data=None, ok=True):
    """Build a lightweight mock that mimics a requests.Response."""
    mock = MagicMock()
    mock.status_code = status_code
    mock.ok = ok
    mock.json.return_value = json_data or {}
    return mock


BARCODE = "028300011304"

BARCODE_API_RESPONSE = {
    "status": 1,
    "product": {
        "product_name": "2% Reduced Fat Milk",
        "brands": "Shamrock Farms",
        "ingredients_text": "Reduced fat milk, vitamins a & d.",
        "quantity": "128oz",
    },
}

NAME_API_RESPONSE = {
    "products": [
        {
            "product_name": "Whole Milk",
            "brands": "Dairy Co",
            "ingredients_text": "Whole milk",
            "quantity": "64oz",
            "code": "111111111111",
        },
        {
            "product_name": "Skim Milk",
            "brands": "Dairy Co",
            "ingredients_text": "Skim milk",
            "quantity": "64oz",
            "code": "222222222222",
        },
    ]
}


# ===========================================================================
# fetch_by_barcode
# ===========================================================================
class TestFetchByBarcode:
    def test_returns_cleaned_dict_on_success(self):
        mock_resp = _mock_response(json_data=BARCODE_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_barcode(BARCODE)
        assert result["product_name"] == "2% Reduced Fat Milk"
        assert result["barcode"] == BARCODE

    def test_returns_none_when_status_zero(self):
        """OpenFoodFacts returns status:0 when a product is not found."""
        mock_resp = _mock_response(json_data={"status": 0})
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_barcode("000000000000")
        assert result is None

    def test_returns_server_unavailable_on_http_error(self):
        mock_resp = _mock_response(status_code=503, ok=False)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_barcode(BARCODE)
        assert result == "server unavailable"

    def test_returned_dict_has_required_keys(self):
        mock_resp = _mock_response(json_data=BARCODE_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_barcode(BARCODE)
        for key in ("product_name", "brands", "ingredients_text", "quantity", "barcode"):
            assert key in result

    def test_correct_url_is_called(self):
        mock_resp = _mock_response(json_data=BARCODE_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp) as mock_get:
            fetch_by_barcode(BARCODE)
        called_url = mock_get.call_args[0][0]
        assert BARCODE in called_url


# ===========================================================================
# fetch_by_name
# ===========================================================================
class TestFetchByName:
    def test_returns_list_on_success(self):
        mock_resp = _mock_response(json_data=NAME_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_name("milk")
        assert isinstance(result, list)
        assert len(result) == 2

    def test_each_item_has_required_keys(self):
        mock_resp = _mock_response(json_data=NAME_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_name("milk")
        for item in result:
            for key in ("product_name", "brands", "ingredients_text", "quantity", "barcode"):
                assert key in item

    def test_barcode_mapped_from_code_field(self):
        """The API returns 'code'; the cleaner should map it to 'barcode'."""
        mock_resp = _mock_response(json_data=NAME_API_RESPONSE)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_name("milk")
        assert result[0]["barcode"] == "111111111111"

    def test_returns_empty_list_when_no_products(self):
        mock_resp = _mock_response(json_data={"products": []})
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_name("xyznotreal")
        assert result == []

    def test_returns_server_unavailable_on_http_error(self):
        mock_resp = _mock_response(status_code=500, ok=False)
        with patch("modules.openfoodfacts.requests.get", return_value=mock_resp):
            result = fetch_by_name("milk")
        assert result == "server unavailable"


# ===========================================================================
# Data cleaner helpers (pure functions — no mocking needed)
# ===========================================================================
class TestBarcodeDataCleaner:
    def test_extracts_product_fields(self):
        result = barcode_data_cleaner(BARCODE, BARCODE_API_RESPONSE)
        assert result["product_name"] == "2% Reduced Fat Milk"
        assert result["brands"] == "Shamrock Farms"
        assert result["barcode"] == BARCODE

    def test_missing_field_returns_none(self):
        """barcode_data_cleaner should gracefully handle missing keys."""
        sparse_data = {"status": 1, "product": {"product_name": "Sparse"}}
        result = barcode_data_cleaner(BARCODE, sparse_data)
        assert result["brands"] is None


class TestNameDataCleaner:
    def test_maps_code_to_barcode(self):
        products = NAME_API_RESPONSE["products"]
        result = name_data_cleaner(products)
        assert result[0]["barcode"] == "111111111111"

    def test_returns_correct_count(self):
        products = NAME_API_RESPONSE["products"]
        result = name_data_cleaner(products)
        assert len(result) == 2

    def test_empty_list_returns_empty(self):
        assert name_data_cleaner([]) == []
