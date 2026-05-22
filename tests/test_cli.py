"""
tests/test_cli.py
------------------
Unit tests for CLI modules: cli/modules/inventory.py, lookup.py, helpers.py.

HTTP calls are intercepted with unittest.mock so the Flask server does not
need to be running.  User input is patched via builtins.input.
"""
import pytest
from unittest.mock import patch, MagicMock, call
import sys, os

CLI_MODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "cli", "modules")
sys.path.insert(0, CLI_MODULES_DIR)


# ---------------------------------------------------------------------------
# Shared mock builder
# ---------------------------------------------------------------------------
def _mock_response(status_code=200, json_data=None):
    mock = MagicMock()
    mock.status_code = status_code
    mock.json.return_value = json_data or {}
    return mock


# ===========================================================================
# helpers.py — request_helper
# ===========================================================================
class TestRequestHelper:
    def test_constructs_correct_url(self):
        from helpers import request_helper
        with patch("helpers.requests.get") as mock_get:
            mock_get.return_value = _mock_response()
            request_helper(path="/inventory", method="get")
        url = mock_get.call_args[0][0]
        assert url == "http://localhost:5555/inventory"

    def test_passes_params(self):
        from helpers import request_helper
        with patch("helpers.requests.get") as mock_get:
            mock_get.return_value = _mock_response()
            request_helper(path="/inventory", method="get", params={"id": 1})
        assert mock_get.call_args[1]["params"] == {"id": 1}

    def test_passes_json_body_for_post(self):
        from helpers import request_helper
        payload = {"product_name": "Test"}
        with patch("helpers.requests.post") as mock_post:
            mock_post.return_value = _mock_response(status_code=201)
            request_helper(path="/inventory", method="post", data=payload)
        assert mock_post.call_args[1]["json"] == payload


# ===========================================================================
# helpers.py — data_unpacker (smoke test — just check it doesn't crash)
# ===========================================================================
class TestDataUnpacker:
    SAMPLE = [
        {"id": 1, "product_name": "Milk", "brands": "Farm", "ingredients_text": "Milk",
         "quantity": "1L", "stock": 10, "price": 2.99, "barcode": "000000000001"}
    ]

    def test_prints_without_error(self, capsys):
        from helpers import data_unpacker
        data_unpacker(self.SAMPLE)
        captured = capsys.readouterr()
        assert "Milk" in captured.out

    def test_handles_single_dict(self, capsys):
        from helpers import data_unpacker
        data_unpacker(self.SAMPLE[0])
        captured = capsys.readouterr()
        assert "Milk" in captured.out


# ===========================================================================
# helpers.py — lookup_data_unpacker
# ===========================================================================
class TestLookupDataUnpacker:
    SAMPLE = [
        {"product_name": "Bread", "brands": "Bakery", "ingredients_text": "Flour",
         "quantity": "20oz", "barcode": "000000000002"}
    ]

    def test_prints_product_name(self, capsys):
        from helpers import lookup_data_unpacker
        lookup_data_unpacker(self.SAMPLE)
        assert "Bread" in capsys.readouterr().out


# ===========================================================================
# helpers.py — selection_list
# ===========================================================================
class TestSelectionList:
    PRODUCTS = [
        {"product_name": "Milk", "brands": "A", "ingredients_text": "", "quantity": "", "barcode": "1"},
        {"product_name": "Bread", "brands": "B", "ingredients_text": "", "quantity": "", "barcode": "2"},
    ]

    def test_returns_selected_product(self):
        from helpers import selection_list
        with patch("builtins.input", return_value="1"):
            result = selection_list(self.PRODUCTS)
        assert result["product_name"] == "Milk"

    def test_returns_none_when_cancelled(self):
        from helpers import selection_list
        with patch("builtins.input", return_value="0"):
            result = selection_list(self.PRODUCTS)
        assert result is None

    def test_re_prompts_on_invalid_input(self):
        from helpers import selection_list
        # First input invalid, second is "0" to cancel
        with patch("builtins.input", side_effect=["99", "0"]):
            result = selection_list(self.PRODUCTS)
        assert result is None


# ===========================================================================
# inventory.py — view_inventory
# ===========================================================================
class TestViewInventory:
    INVENTORY = [
        {"id": 1, "product_name": "Milk", "brands": "Farm", "ingredients_text": "Milk",
         "quantity": "1L", "stock": 5, "price": 1.99, "barcode": "000000000001"}
    ]

    def test_displays_inventory(self, capsys):
        from inventory import view_inventory
        mock_resp = _mock_response(json_data=self.INVENTORY)
        with patch("helpers.requests.get", return_value=mock_resp):
            with patch("builtins.input", return_value=""):  # ENTER to continue
                view_inventory()
        assert "Milk" in capsys.readouterr().out


# ===========================================================================
# inventory.py — add_item
# ===========================================================================
class TestAddItem:
    INPUTS = ["Test Product", "Brand", "Ingredients", "10oz", "20", "1.99", "123456789012"]
    NEW_PRODUCT = {"id": 4, "product_name": "Test Product", "brands": "Brand",
                   "ingredients_text": "Ingredients", "quantity": "10oz",
                   "stock": 20, "price": 1.99, "barcode": "123456789012"}

    def test_prints_success_on_201(self, capsys):
        from inventory import add_item
        mock_resp = _mock_response(status_code=201, json_data=self.NEW_PRODUCT)
        with patch("builtins.input", side_effect=self.INPUTS):
            with patch("helpers.requests.post", return_value=mock_resp):
                add_item()
        assert "Test Product" in capsys.readouterr().out

    def test_prints_error_on_400(self, capsys):
        from inventory import add_item
        mock_resp = _mock_response(status_code=400, json_data={"message": "Invalid price"})
        with patch("builtins.input", side_effect=self.INPUTS):
            with patch("helpers.requests.post", return_value=mock_resp):
                add_item()
        assert "Failed" in capsys.readouterr().out


# ===========================================================================
# inventory.py — delete_item
# ===========================================================================
class TestDeleteItem:
    PRODUCT = {"id": 1, "product_name": "Milk", "brands": "Farm", "ingredients_text": "Milk",
               "quantity": "1L", "stock": 5, "price": 1.99, "barcode": "000000000001"}

    def test_deletes_on_confirmation(self, capsys):
        from inventory import delete_item
        get_resp = _mock_response(json_data=self.PRODUCT)
        del_resp = _mock_response(json_data={"message": "Inventory item deleted"})

        with patch("helpers.requests.get", return_value=get_resp):
            with patch("helpers.requests.delete", return_value=del_resp):
                with patch("builtins.input", side_effect=["1", "delete"]):
                    delete_item()
        assert "deleted" in capsys.readouterr().out

    def test_aborts_on_back_command(self, capsys):
        from inventory import delete_item
        get_resp = _mock_response(json_data=self.PRODUCT)

        with patch("helpers.requests.get", return_value=get_resp):
            with patch("builtins.input", side_effect=["1", "b"]):
                delete_item()  # should return without calling delete


# ===========================================================================
# lookup.py — barcode_search
# ===========================================================================
class TestBarcodeSearch:
    PRODUCT = {"product_name": "Milk", "brands": "Farm", "ingredients_text": "Milk",
               "quantity": "1L", "barcode": "000000000001"}

    def test_success_path_shows_product(self, capsys):
        from lookup import barcode_search
        mock_resp = _mock_response(status_code=200, json_data=self.PRODUCT)
        with patch("helpers.requests.get", return_value=mock_resp):
            with patch("builtins.input", side_effect=["000000000001", "n"]):
                barcode_search()
        assert "Milk" in capsys.readouterr().out

    def test_404_prints_not_found(self, capsys):
        from lookup import barcode_search
        not_found_resp = _mock_response(status_code=404)
        found_resp = _mock_response(status_code=200, json_data=self.PRODUCT)
        with patch("helpers.requests.get", side_effect=[not_found_resp, found_resp]):
            with patch("builtins.input", side_effect=["bad", "000000000001", "n"]):
                barcode_search()
        assert "not found" in capsys.readouterr().out.lower()

    def test_502_prints_unavailable(self, capsys):
        from lookup import barcode_search
        unavail_resp = _mock_response(status_code=502)
        found_resp = _mock_response(status_code=200, json_data=self.PRODUCT)
        with patch("helpers.requests.get", side_effect=[unavail_resp, found_resp]):
            with patch("builtins.input", side_effect=["bad", "000000000001", "n"]):
                barcode_search()
        assert "unavailable" in capsys.readouterr().out.lower()


# ===========================================================================
# lookup.py — name_search
# ===========================================================================
class TestNameSearch:
    PRODUCTS = [
        {"product_name": "Whole Milk", "brands": "Dairy Co", "ingredients_text": "Milk",
         "quantity": "64oz", "barcode": "111111111111"},
    ]

    def test_shows_results_and_prompts_selection(self, capsys):
        from lookup import name_search
        mock_resp = _mock_response(status_code=200, json_data=self.PRODUCTS)
        with patch("helpers.requests.get", return_value=mock_resp):
            with patch("builtins.input", side_effect=["milk", "1", "n"]):
                name_search()
        assert "Whole Milk" in capsys.readouterr().out

    def test_handles_cancel_selection(self, capsys):
        from lookup import name_search
        mock_resp = _mock_response(status_code=200, json_data=self.PRODUCTS)
        with patch("helpers.requests.get", return_value=mock_resp):
            with patch("builtins.input", side_effect=["milk", "0"]):
                name_search()  # should not raise
