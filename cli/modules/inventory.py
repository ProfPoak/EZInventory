from .helpers import request_helper, data_unpacker

def view_inventory():
    response = request_helper(path="/inventory", method="get").json()
    data_unpacker(response)
    input("Press ENTER to continue")
    

def view_item():
    while True:
        id = input("Enter product ID (or 'b' to go back): ").strip()
        if id.lower() == "b":
            break
        response = request_helper(path=f'/inventory/{id}', method="get")
        if response.status_code == 404:
            print("\nProduct not found. Please try again.")
        else:
            data_unpacker([response.json()])
            input("Press ENTER to continue")
            break

def add_item():
    product_name = input("Enter Product Name: ")
    brands = input("Enter Brand: ")
    ingredients_text = input("Enter Ingredients: ")
    quantity = input("Enter Product Size: ")
    stock = input("Enter Stock: ")
    price = input("Enter Price: ")
    barcode = input("Enter UPC Barcode: ")

    new_product = {
        "product_name" : product_name,
        "brands" : brands,
        "ingredients_text" : ingredients_text,
        "quantity" : quantity,
        "stock" : stock,
        "price" : price,
        "barcode" : barcode
    }

    response = request_helper(path="/inventory", method="post", data=new_product)
    r = response.json()
    if response.status_code == 201:
        print(f"\n'{r['product_name']}' has been added to inventory with ID: {r['id']}")
    else:
        print("\nFailed to add product.")

def update_item():
    pass

def delete_item():
    pass
