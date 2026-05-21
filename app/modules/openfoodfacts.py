import requests
import logging

logging.basicConfig(
    filename="logs/api.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

HEADERS = {"User-Agent": "EZInventory - Python - Version 1.0 - https://github.com/profpoak/EZInventory"}

def fetch_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json"
    params = {
        "fields": "product_name,brands,ingredients_text,quantity,code",
        "lc": "en"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    logging.info(f"Barcode lookup {barcode}: {response.status_code}")
    if not response.ok:
        logging.error(f"Barcode lookup failed: {response.status_code}")
        return "server unavailable"
    data = response.json()
    if data.get("status") == 0:
        return None
    return barcode_data_cleaner(barcode, data)

def fetch_by_name(name):
    url = "https://world.openfoodfacts.org/cgi/search.pl"
    params = {
    "search_terms": name,
    "search_simple": 1,
    "action": "process",
    "json": 1,
    "page_size": 5,
    "fields": "product_name,brands,ingredients_text,quantity,code",
    "lc": "en",
    "countries_tags": "united-states"
    }
    response = requests.get(url, headers=HEADERS, params=params)
    logging.info(f"Name search '{name}': {response.status_code}")
    if not response.ok:
        logging.error(f"Name search failed: {response.status_code}")
        return "server unavailable"
    data = response.json()
    products = data.get("products", [])
    return name_data_cleaner(products)

def barcode_data_cleaner(barcode, data):
    product = data.get("product", {})
    return {
        "product_name": product.get("product_name"),
        "brands": product.get("brands"),
        "ingredients_text": product.get("ingredients_text"),
        "quantity": product.get("quantity"),
        "barcode": barcode
    }

def name_data_cleaner(products):
    clean_products = []
    for data in products:
        clean_products.append({
        "product_name": data.get("product_name"),
        "brands": data.get("brands"),
        "ingredients_text": data.get("ingredients_text"),
        "quantity": data.get("quantity"),
        "barcode": data.get("code")
    })

    return clean_products