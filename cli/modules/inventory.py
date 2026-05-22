from .helpers import request_helper, data_unpacker, product_lookup

def view_inventory():
    response = request_helper(path="/inventory", method="get").json()
    data_unpacker(response)
    input("Press ENTER to continue")
    

def view_item():
    id, response = product_lookup()
    if id is None:
        return
   
    data_unpacker(response.json())     
    input("Press ENTER to continue")

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
        print(f"Error: {r.get('message', 'Unknown error')}")

def update_item():
    id, response = product_lookup(action="Update")
    if id is None:
        return

    while True:
        response = request_helper(path=f'/inventory/{id}', method="get")
        p = response.json()

        fields = {
            "1": (f"Product Name: {p['product_name']}", "product_name"),
            "2": (f"Brand: {p['brands']}", "brands"),
            "3": (f"Ingredients: {p['ingredients_text']}", "ingredients_text"),
            "4": (f"Product Size: {p['quantity']}", "quantity"),
            "5": (f"Stock: {p['stock']}", "stock"),
            "6": (f"Price: ${p['price']}", "price"),
            "7": (f"UPC Barcode: {p['barcode']}", "barcode"),
        }


        print("\nWhat would you like to update?")
        for key, (label, _) in fields.items():
            print(f"{key}. {label}")
        print("0. Done")

        choice = input("\nEnter your selection: ").strip()
        
        if choice == "0":
            break
        elif choice not in fields:
            print("\nInvalid choice.")
            continue
        
        # TODO: Refactor input prompt to show field name only, not current value
        label, field_key = fields[choice]
        new_value = input(f"Enter new {label}: ").strip()

        response = request_helper(path=f'/inventory/{id}', method="patch", data={field_key: new_value})
        r = response.json()
        if response.status_code == 200:
            # TODO: Refactor success message to show old value -> new value
            print(f"\n'{label}' updated successfully.")
        else:
            print("\nFailed to update product.")
            print(f"Error: {r.get('message', 'Unknown error')}")

def delete_item():
    id, response = product_lookup(action="Delete")
    if id is None:
        return
    
    while True:
        confirmation = input("Type 'delete' to confirm request (or 'b' to go back): ")
        if confirmation.lower() == "b":
                break
        elif confirmation == "delete":    
            response = request_helper(path=f'/inventory/{id}', method="delete")
            r = response.json()
            if response.status_code == 200:
                print("\nProduct deleted successfully.")
                break
            else:
                print("\n Unable to delete product please try again")
                print(f"Error: {r.get('message', 'Unknown error')}")
                break
        else:
            print("\nInvalid response please try again.")
