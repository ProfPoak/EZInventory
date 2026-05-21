import requests

HEADERS = {"User-Agent": "EZInventory/1.0"}

def fetch_by_barcode(barcode):
    url = f"https://world.openfoodfacts.org/api/v2/product/{barcode}.json?fields=product_name,brands,ingredients_text,quantity,code&lc=en"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    if data.get("status") == 0:
        return None
    clean_data = barcode_data_cleaner(barcode, data)
    return clean_data

def fetch_by_name(name):
    url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={name}&json=1&page_size=5&fields=product_name,brands,ingredients_text,quantity,code&lc=en&countries_tags=united-states"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    products = data.get("products", [])
    clean_data = name_data_cleaner(products)
    return clean_data

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