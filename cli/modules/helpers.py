import requests

def request_helper(path, method, data=None, params=None):
    url = f"http://localhost:5555{path}"
    response = getattr(requests, method.lower())(url, json=data, params=params)
    return response

# TODO: Refactor data_unpacker to handle both single dict and list like lookup_data_unpacker
# so callers don't need to manually wrap single items in a list
def data_unpacker(data):
    print("\nInventory:")
    for p in data:
            print(f'  ID: {p["id"]}')
            print(f'  Product Name: {p["product_name"]}')
            print(f'  Brands: {p["brands"]}')
            print(f'  Ingredients: {p["ingredients_text"]}')
            print(f'  Product Size: {p["quantity"]}')
            print(f'  Stock: {p["stock"]}')
            print(f'  Price: ${p["price"]}')
            print(f'  UPC Barcode: {p["barcode"]}')
            print("  ---")
            print("\n")

def product_lookup(action="View"):
    while True:
        id = input(f"Enter product ID to {action} (or 'b' to go back): ").strip()
        if id.lower() == "b":
            return None, None
        
        response = request_helper(path=f'/inventory/{id}', method="get")
        if response.status_code == 404:
            print("\nProduct not found. Please try again.")
        else:
            return id, response
        
def lookup_data_unpacker(data):
    print("\nResults:")
    items = data if isinstance(data, list) else [data]
    for p in items:
        print(f'  Product Name: {p["product_name"]}')
        print(f'  Brands: {p["brands"]}')
        print(f'  Ingredients: {p["ingredients_text"]}')
        print(f'  Product Size: {p["quantity"]}')
        print(f'  UPC Barcode: {p["barcode"]}')
        print("  ---")

def lookup_add_item(data):
    while True:
        confirmation = input("Would you like to save this product? (y/n): ")
        
        if confirmation.lower() == "y":
            stock = input("Enter Stock: ")
            price = input("Enter Price: ")
            new_product = {
                "product_name" : data["product_name"],
                "brands" : data["brands"],
                "ingredients_text" : data["ingredients_text"],
                "quantity" : data["quantity"],
                "stock" : stock,
                "price" : price,
                "barcode": data["barcode"]
            }

            response = request_helper(path="/inventory", method="post", data=new_product)
            r = response.json()
            if response.status_code == 201:
                print(f"\n'{r['product_name']}' has been added to inventory with ID: {r['id']}")
                return
            else:
                print("\nFailed to add product.")
                return
        elif confirmation.lower() == "n":
            print("Product not saved.")
            return
        else:
            print("Invalid input. Please enter 'y' or 'n'.")