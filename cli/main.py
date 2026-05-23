import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "modules"))

import requests
from modules.inventory import view_inventory, view_item, add_item, update_item, delete_item
from modules.lookup import lookup_product

def main():
    menu = {
        "1": ("View all inventory", view_inventory),
        "2": ("View item by ID", view_item),
        "3": ("Add item manually", add_item),
        "4": ("Update item", update_item),
        "5": ("Delete item", delete_item),
        "6": ("Lookup product", lookup_product),
        "0": ("Exit", None)
    }

    while True:
        print("\n --- EZInventory ---")
        for key, (label, _) in menu.items():
            print(f"{key}. {label}")

        choice = input("\nEnter your selection: ").strip()

        if choice == "0":
            print("Goodbye!")
            break
        elif choice in menu:
            _, func = menu[choice]
            func()
        else:
            print("Invalid choice. Please select an option from the list.")

if __name__ == "__main__":
    main()