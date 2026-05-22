"""
tests/test_product_model.py
----------------------------
Unit tests for app/classes/Product.py.

Validates that:
  - A valid Product can be created and serialised with to_dict()
  - Each property setter raises the correct exception type and message
    when given bad data.
"""
import pytest
import sys, os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "app"))
from classes.Product import Product


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
VALID_KWARGS = {
    "id": 1,
    "product_name": "Good Product",
    "brands": "Good Brand",
    "ingredients_text": "Water, salt",
    "quantity": "16 oz",
    "stock": 10,
    "price": 1.99,
    "barcode": "012345678901",
}


def make_product(**overrides):
    kwargs = {**VALID_KWARGS, **overrides}
    return Product(**kwargs)


# ===========================================================================
# Happy-path construction
# ===========================================================================
class TestProductCreation:
    def test_creates_successfully_with_valid_data(self):
        p = make_product()
        assert p.product_name == "Good Product"

    def test_to_dict_returns_all_keys(self):
        p = make_product()
        d = p.to_dict()
        expected = {"id", "product_name", "brands", "ingredients_text",
                    "quantity", "stock", "price", "barcode"}
        assert expected == set(d.keys())

    def test_to_dict_values_match(self):
        p = make_product()
        d = p.to_dict()
        assert d["product_name"] == "Good Product"
        assert d["price"] == 1.99
        assert d["barcode"] == "012345678901"

    def test_stock_stored_as_int(self):
        # stock given as string "10" should be coerced to int
        p = make_product(stock="10")
        assert isinstance(p.stock, int)


# ===========================================================================
# product_name validation
# ===========================================================================
class TestProductNameValidation:
    def test_raises_type_error_for_non_string(self):
        with pytest.raises(TypeError, match="Product name must be a string"):
            make_product(product_name=123)

    def test_raises_type_error_for_none(self):
        with pytest.raises(TypeError):
            make_product(product_name=None)

    def test_raises_value_error_for_empty_string(self):
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            make_product(product_name="")

    def test_raises_value_error_for_whitespace_only(self):
        with pytest.raises(ValueError, match="Product name cannot be empty"):
            make_product(product_name="   ")


# ===========================================================================
# brands validation
# ===========================================================================
class TestBrandsValidation:
    def test_raises_type_error_for_non_string(self):
        with pytest.raises(TypeError, match="Brands must be a string"):
            make_product(brands=42)

    def test_raises_value_error_for_empty_string(self):
        with pytest.raises(ValueError, match="Brands cannot be empty"):
            make_product(brands="")

    def test_raises_value_error_for_whitespace_only(self):
        with pytest.raises(ValueError, match="Brands cannot be empty"):
            make_product(brands="   ")


# ===========================================================================
# ingredients_text validation
# ===========================================================================
class TestIngredientsTextValidation:
    def test_raises_type_error_for_non_string(self):
        with pytest.raises(TypeError, match="Ingredients text must be a string"):
            make_product(ingredients_text=["flour", "water"])

    def test_raises_value_error_for_empty_string(self):
        with pytest.raises(ValueError, match="Ingredients cannot be empty"):
            make_product(ingredients_text="")

    def test_raises_value_error_for_whitespace_only(self):
        with pytest.raises(ValueError, match="Ingredients cannot be empty"):
            make_product(ingredients_text="   ")


# ===========================================================================
# quantity validation
# ===========================================================================
class TestQuantityValidation:
    def test_raises_type_error_for_non_string(self):
        with pytest.raises(TypeError, match="Quantity must be a string"):
            make_product(quantity=16)

    def test_raises_value_error_for_empty_string(self):
        with pytest.raises(ValueError, match="Quantity cannot be empty"):
            make_product(quantity="")

    def test_raises_value_error_for_whitespace_only(self):
        with pytest.raises(ValueError, match="Quantity cannot be empty"):
            make_product(quantity="   ")


# ===========================================================================
# stock validation
# ===========================================================================
class TestStockValidation:
    def test_raises_type_error_for_none(self):
        with pytest.raises(TypeError, match="Stock cannot be left empty"):
            make_product(stock=None)

    def test_raises_type_error_for_non_numeric_string(self):
        with pytest.raises(TypeError, match="Stock must be an integer"):
            make_product(stock="abc")

    def test_raises_value_error_for_zero(self):
        with pytest.raises(ValueError, match="Stock must be a positive integer"):
            make_product(stock=0)

    def test_raises_value_error_for_negative(self):
        with pytest.raises(ValueError, match="Stock must be a positive integer"):
            make_product(stock=-1)

    def test_accepts_string_integer(self):
        p = make_product(stock="5")
        assert p.stock == 5


# ===========================================================================
# price validation
# ===========================================================================
class TestPriceValidation:
    def test_raises_type_error_for_none(self):
        with pytest.raises(TypeError, match="Price cannot be left empty"):
            make_product(price=None)

    def test_raises_type_error_for_non_numeric_string(self):
        with pytest.raises(TypeError, match="Price must be a number"):
            make_product(price="free")

    def test_raises_value_error_for_zero(self):
        with pytest.raises(ValueError, match="Price must be a positive number"):
            make_product(price=0)

    def test_raises_value_error_for_negative(self):
        with pytest.raises(ValueError, match="Price must be a positive number"):
            make_product(price=-0.01)

    def test_accepts_string_float(self):
        p = make_product(price="2.99")
        assert p.price == pytest.approx(2.99)

    def test_price_is_rounded_to_two_decimal_places(self):
        p = make_product(price=1.999999)
        assert p.price == 2.0

    def test_price_stored_as_float(self):
        p = make_product(price="3.50")
        assert isinstance(p.price, float)


# ===========================================================================
# barcode validation
# ===========================================================================
class TestBarcodeValidation:
    def test_raises_type_error_for_none(self):
        with pytest.raises(TypeError):
            make_product(barcode=None)

    def test_raises_type_error_for_bool(self):
        with pytest.raises(TypeError):
            make_product(barcode=True)

    def test_raises_type_error_for_string_with_dashes(self):
        with pytest.raises(TypeError):
            make_product(barcode="012-345-6789012")

    def test_raises_type_error_for_alpha_string(self):
        with pytest.raises(TypeError):
            make_product(barcode="ABCDEFGHIJKL")

    def test_raises_value_error_for_too_short(self):
        with pytest.raises(ValueError, match="Barcode must be 12 or 13 characters long"):
            make_product(barcode="12345")

    def test_raises_value_error_for_too_long(self):
        with pytest.raises(ValueError, match="Barcode must be 12 or 13 characters long"):
            make_product(barcode="12345678901234")

    def test_accepts_12_digit_barcode(self):
        p = make_product(barcode="012345678901")
        assert p.barcode == "012345678901"

    def test_accepts_13_digit_barcode(self):
        p = make_product(barcode="0123456789012")
        assert p.barcode == "0123456789012"

    def test_accepts_integer_barcode_coerced_to_string(self):
        p = make_product(barcode=123456789012)
        assert p.barcode == "123456789012"
