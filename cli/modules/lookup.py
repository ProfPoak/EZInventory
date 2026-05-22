from .helpers import request_helper, lookup_data_unpacker, lookup_add_item

def lookup_product():
    menu = {
        "1": ("Search by Barcode", barcode_search),
        "2": ("Search by Name", name_search),
        "0": ("Exit", None)
    }

    while True:
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")

        choice = input("\nEnter your selection: ").strip()

        if choice == "0":
            break
        elif choice in menu:
            _, func = menu[choice]
            func()
        else:
            print("Invalid choice. Please select an option from the list.")

def barcode_search():
    while True:
        search = input("\n Enter UPC barcode: ")
        response = request_helper(path='/inventory/lookup', method="get", params={"barcode": search})
        if response.status_code == 404:
            print("Product not found. Please try a different barcode.")
        elif response.status_code == 502:
            print("Server is currently unavailable. Please try again later")
        elif response.status_code == 200:
            data = response.json()
            lookup_data_unpacker(data)
            lookup_add_item(data)
            return

def name_search():
    pass