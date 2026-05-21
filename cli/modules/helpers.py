import requests

def request_helper(path, method, data=None):
        url = f"http://localhost:5555{path}"
        response = getattr(requests, method.lower())(url, json=data)
        return response

def data_unpacker(data):
        print("\nInventory:")
        for p in data:
                print(f'  ID: {p["id"]}')
                print(f'  Product Name: {p["product_name"]}')
                print(f'  Brands: {p["brands"]}')
                print(f'  Ingredients: {p["ingredients_text"]}')
                print(f'  Product Size: {p["quantity"]}')
                print(f'  Stock: {p["stock"]}')
                print(f'  Price: {p["price"]}')
                print(f'  UPC Barcode: {p["barcode"]}')
                print("  ---")
                print("\n")
   