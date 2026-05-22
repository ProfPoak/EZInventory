"""
tests/test_api_endpoints.py
----------------------------
Unit tests for every Flask route in app/app.py.

Covers:
  GET  /inventory
  GET  /inventory/<id>
  POST /inventory
  PATCH /inventory/<id>
  DELETE /inventory/<id>
  GET  /inventory/lookup  (barcode + name variants)
"""
import pytest
from unittest.mock import patch


# ===========================================================================
# GET /inventory
# ===========================================================================
class TestGetInventory:
    def test_returns_200(self, client):
        response = client.get("/inventory")
        assert response.status_code == 200

    def test_returns_list(self, client):
        data = response = client.get("/inventory").get_json()
        assert isinstance(data, list)

    def test_returns_seeded_items(self, client):
        data = client.get("/inventory").get_json()
        assert len(data) == 3

    def test_item_has_expected_keys(self, client):
        data = client.get("/inventory").get_json()
        expected_keys = {"id", "product_name", "brands", "ingredients_text",
                         "quantity", "stock", "price", "barcode"}
        assert expected_keys.issubset(data[0].keys())


# ===========================================================================
# GET /inventory/<id>
# ===========================================================================
class TestGetInventoryById:
    def test_returns_200_for_existing_id(self, client):
        response = client.get("/inventory/1")
        assert response.status_code == 200

    def test_returns_correct_product(self, client):
        data = client.get("/inventory/1").get_json()
        assert data["product_name"] == "2% Reduced Fat Milk"

    def test_returns_404_for_missing_id(self, client):
        response = client.get("/inventory/999")
        assert response.status_code == 404

    def test_404_response_has_message(self, client):
        data = client.get("/inventory/999").get_json()
        assert "message" in data


# ===========================================================================
# POST /inventory
# ===========================================================================
class TestCreateProduct:
    def test_returns_201_on_success(self, client, sample_product):
        response = client.post("/inventory", json=sample_product)
        assert response.status_code == 201

    def test_returned_product_has_assigned_id(self, client, sample_product):
        data = client.post("/inventory", json=sample_product).get_json()
        assert "id" in data
        assert isinstance(data["id"], int)

    def test_product_is_added_to_inventory(self, client, sample_product):
        client.post("/inventory", json=sample_product)
        all_items = client.get("/inventory").get_json()
        names = [p["product_name"] for p in all_items]
        assert sample_product["product_name"] in names

    def test_ids_auto_increment(self, client, sample_product):
        # Seed data has ids 1-3; the next assigned id must be 4
        data = client.post("/inventory", json=sample_product).get_json()
        assert data["id"] == 4

    def test_returns_400_when_product_name_missing(self, client, sample_product):
        del sample_product["product_name"]
        response = client.post("/inventory", json=sample_product)
        assert response.status_code == 400

    def test_returns_400_for_invalid_stock(self, client, sample_product):
        sample_product["stock"] = -5
        response = client.post("/inventory", json=sample_product)
        assert response.status_code == 400

    def test_returns_400_for_invalid_price(self, client, sample_product):
        sample_product["price"] = 0
        response = client.post("/inventory", json=sample_product)
        assert response.status_code == 400

    def test_returns_400_for_non_numeric_barcode(self, client, sample_product):
        sample_product["barcode"] = "ABC-DEF"
        response = client.post("/inventory", json=sample_product)
        assert response.status_code == 400


# ===========================================================================
# PATCH /inventory/<id>
# ===========================================================================
class TestUpdateProduct:
    def test_returns_200_on_success(self, client):
        response = client.patch("/inventory/1", json={"stock": 999})
        assert response.status_code == 200

    def test_field_is_updated(self, client):
        client.patch("/inventory/1", json={"stock": 999})
        data = client.get("/inventory/1").get_json()
        assert data["stock"] == 999

    def test_other_fields_unchanged(self, client):
        client.patch("/inventory/1", json={"stock": 999})
        data = client.get("/inventory/1").get_json()
        assert data["product_name"] == "2% Reduced Fat Milk"

    def test_returns_404_for_missing_id(self, client):
        response = client.patch("/inventory/999", json={"stock": 5})
        assert response.status_code == 404

    def test_returns_400_or_415_for_missing_body(self, client):
        # Flask rejects a PATCH with no Content-Type header as 415 before
        # our code even runs.  Accept either 400 or 415 as "bad request".
        response = client.patch("/inventory/1")
        assert response.status_code in (400, 415)

    def test_returns_400_for_invalid_price_update(self, client):
        response = client.patch("/inventory/1", json={"price": -1})
        assert response.status_code == 400

    def test_can_update_product_name(self, client):
        client.patch("/inventory/2", json={"product_name": "Updated Chocolate"})
        data = client.get("/inventory/2").get_json()
        assert data["product_name"] == "Updated Chocolate"


# ===========================================================================
# DELETE /inventory/<id>
# ===========================================================================
class TestDeleteProduct:
    def test_returns_200_on_success(self, client):
        response = client.delete("/inventory/1")
        assert response.status_code == 200

    def test_product_removed_from_inventory(self, client):
        client.delete("/inventory/1")
        response = client.get("/inventory/1")
        assert response.status_code == 404

    def test_inventory_count_decreases(self, client):
        before = len(client.get("/inventory").get_json())
        client.delete("/inventory/1")
        after = len(client.get("/inventory").get_json())
        assert after == before - 1

    def test_returns_404_for_missing_id(self, client):
        response = client.delete("/inventory/999")
        assert response.status_code == 404

    def test_response_contains_message(self, client):
        data = client.delete("/inventory/1").get_json()
        assert "message" in data


# ===========================================================================
# GET /inventory/lookup  (barcode)
# ===========================================================================
class TestLookupByBarcode:
    MOCK_PRODUCT = {
        "product_name": "Mock Milk",
        "brands": "Mock Farm",
        "ingredients_text": "Milk",
        "quantity": "64oz",
        "barcode": "000000000001",
    }

    def test_returns_200_with_valid_barcode(self, client):
        with patch("app.fetch_by_barcode", return_value=self.MOCK_PRODUCT):
            response = client.get("/inventory/lookup?barcode=000000000001")
        assert response.status_code == 200

    def test_returns_product_data(self, client):
        with patch("app.fetch_by_barcode", return_value=self.MOCK_PRODUCT):
            data = client.get("/inventory/lookup?barcode=000000000001").get_json()
        assert data["product_name"] == "Mock Milk"

    def test_returns_404_when_barcode_not_found(self, client):
        with patch("app.fetch_by_barcode", return_value=None):
            response = client.get("/inventory/lookup?barcode=000000000000")
        assert response.status_code == 404

    def test_returns_502_when_server_unavailable(self, client):
        with patch("app.fetch_by_barcode", return_value="server unavailable"):
            response = client.get("/inventory/lookup?barcode=000000000000")
        assert response.status_code == 502


# ===========================================================================
# GET /inventory/lookup  (name)
# ===========================================================================
class TestLookupByName:
    MOCK_RESULTS = [
        {
            "product_name": "Mock Bread",
            "brands": "Mock Bakery",
            "ingredients_text": "Flour, water",
            "quantity": "20oz",
            "barcode": "000000000002",
        }
    ]

    def test_returns_200_with_valid_name(self, client):
        with patch("app.fetch_by_name", return_value=self.MOCK_RESULTS):
            response = client.get("/inventory/lookup?name=bread")
        assert response.status_code == 200

    def test_returns_list_of_products(self, client):
        with patch("app.fetch_by_name", return_value=self.MOCK_RESULTS):
            data = client.get("/inventory/lookup?name=bread").get_json()
        assert isinstance(data, list)

    def test_returns_404_when_no_results(self, client):
        with patch("app.fetch_by_name", return_value=[]):
            response = client.get("/inventory/lookup?name=xyznotreal")
        assert response.status_code == 404

    def test_returns_502_when_server_unavailable(self, client):
        with patch("app.fetch_by_name", return_value="server unavailable"):
            response = client.get("/inventory/lookup?name=milk")
        assert response.status_code == 502

    def test_returns_400_with_no_params(self, client):
        response = client.get("/inventory/lookup")
        assert response.status_code == 400
