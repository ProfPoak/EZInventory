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
    pass

def update_item():
    pass

def delete_item():
    pass
