"""
Shared pytest fixtures for the EZInventory test suite.
"""
import pytest
import sys
import os

# ---------------------------------------------------------------------------
# Path setup — makes `app` and `cli` importable without installing the package
# ---------------------------------------------------------------------------
APP_DIR = os.path.join(os.path.dirname(__file__), "..", "app")
CLI_DIR = os.path.join(os.path.dirname(__file__), "..", "cli")
CLI_MODULES_DIR = os.path.join(os.path.dirname(__file__), "..", "cli", "modules")
sys.path.insert(0, APP_DIR)
sys.path.insert(0, CLI_DIR)
sys.path.insert(0, CLI_MODULES_DIR)

# ---------------------------------------------------------------------------
# Flask test client
# ---------------------------------------------------------------------------
@pytest.fixture
def app():
    """Return a configured Flask app in testing mode with a fresh inventory."""
    import app as app_module          # app/app.py  (the module, not the Flask object)
    import db.db as db_module

    flask_app = app_module.app
    flask_app.config["TESTING"] = True

    seed = [
        {
            "id": 1,
            "product_name": "2% Reduced Fat Milk",
            "brands": "Shamrock Farms",
            "ingredients_text": "Reduced fat milk, vitamins a & d.",
            "quantity": "128oz",
            "stock": 100,
            "price": 4.99,
            "barcode": "028300011304",
        },
        {
            "id": 2,
            "product_name": "Kisses Chocolate Candy Assortment",
            "brands": "Hershey's",
            "ingredients_text": "Milk chocolate (sugar, milk, chocolate, cocoa butter, lactose, milk fat, soy lecithin, PGPR, vanillin)",
            "quantity": "35.5 oz",
            "stock": 50,
            "price": 1.99,
            "barcode": "034000130030",
        },
        {
            "id": 3,
            "product_name": "Calcium Fortified Enriched Bread",
            "brands": "Wonder",
            "ingredients_text": "Enriched flour, water, high fructose corn syrup, yeast, soybean oil, salt",
            "quantity": "20 oz",
            "stock": 30,
            "price": 3.49,
            "barcode": "072250011372",
        },
    ]

    # app/app.py does `from db.db import inventory` — that name in the app
    # module points at the same list object as db_module.inventory.
    # We must mutate that object in-place (slice assignment) rather than
    # rebinding the db_module attribute, so app_module.inventory stays in sync.
    app_module.inventory[:] = seed
    db_module.inventory[:] = seed

    yield flask_app


@pytest.fixture
def client(app):
    """Return a Flask test client."""
    return app.test_client()


# ---------------------------------------------------------------------------
# Reusable sample product payload
# ---------------------------------------------------------------------------
@pytest.fixture
def sample_product():
    return {
        "product_name": "Test Crackers",
        "brands": "Test Brand",
        "ingredients_text": "Flour, salt, water",
        "quantity": "10 oz",
        "stock": 20,
        "price": 2.49,
        "barcode": "123456789012",
    }
