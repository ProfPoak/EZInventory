# EZInventory

A Python REST API built with Flask for managing product inventory. Includes a CLI for interacting with the API and integration with the OpenFoodFacts API for product lookups.

---

## Installation & Setup

**Requirements:** Python 3.8+, pipenv

```bash
git clone https://github.com/profpoak/EZInventory.git
cd EZInventory
pipenv install
pipenv shell
```

**Start the server:**
```bash
cd app
python app.py
```
Server runs on `http://localhost:5555`.

**Start the CLI** (in a separate terminal):
```bash
cd cli
python main.py
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/inventory` | Return all inventory items |
| GET | `/inventory/<id>` | Return a single item by ID |
| POST | `/inventory` | Add a new item |
| PATCH | `/inventory/<id>` | Update fields on an existing item |
| DELETE | `/inventory/<id>` | Delete an item |
| GET | `/inventory/lookup?barcode=<upc>` | Look up a product by UPC barcode |
| GET | `/inventory/lookup?name=<name>` | Search for a product by name |

**POST/PATCH request body fields:**
```json
{
  "product_name": "string",
  "brands": "string",
  "ingredients_text": "string",
  "quantity": "string",
  "stock": 10,
  "price": 2.99,
  "barcode": "012345678901"
}
```

---

## CLI Usage

After starting the server, run `python main.py` from the `cli/` directory.

```
 --- EZInventory ---
1. View all inventory
2. View item by ID
3. Add item manually
4. Update item
5. Delete item
6. Lookup product
0. Exit
```

**Lookup product** searches OpenFoodFacts by barcode or name and gives you the option to save the result directly to inventory.

---

## Running Tests

```bash
pytest
```

Tests are organized in `tests/` and cover the Product model, all API endpoints, CLI modules, and the OpenFoodFacts integration.
