from flask import Flask, jsonify, request
from db.db import inventory
from classes.Product import Product
from modules.openfoodfacts import fetch_by_barcode, fetch_by_name

app = Flask(__name__)

@app.errorhandler(TypeError)
@app.errorhandler(ValueError)
def handle_validation_error(e):
    return jsonify({"message": str(e)}), 400

@app.errorhandler(KeyError)
def handle_key_error(e):
    return jsonify({"message": f"Missing required field {str(e)}"}), 400

@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200

@app.route("/inventory/<int:id>", methods=["GET"])
def get_inventory_by_id(id):
    for i in inventory:
        if i["id"] == id:
            return jsonify(i), 200
    return jsonify({"message": "Inventory item not found"}), 404

@app.route("/inventory", methods=["POST"])
def create_product():
    data = request.get_json()
    new_product_id = max((p["id"] for p in inventory), default=0) + 1
    new_product = Product(
        id=new_product_id, 
        product_name=data["product_name"],
        brands=data["brands"],
        ingredients_text=data["ingredients_text"],
        quantity=data["quantity"],
        stock=data["stock"],
        price=data["price"],
        barcode=data["barcode"]
    )
    inventory.append(new_product.to_dict())
    return jsonify(new_product.to_dict()), 201


@app.route("/inventory/<int:id>", methods=["PATCH"])
def update_product(id):
    product_dict = next((p for p in inventory if p["id"] == id), None)
    if not product_dict:
        return jsonify({"message": "Inventory item not found"}), 404
    
    data = request.get_json()
    if not data:
        return jsonify({"message": "Missing request body"}), 400
    
    merged_data = {**product_dict, **data}
    validated_product = Product(
        product_name=merged_data.get("product_name"),
        brands=merged_data.get("brands"),
        ingredients_text=merged_data.get("ingredients_text"),
        quantity=merged_data.get("quantity"),
        stock=merged_data.get("stock"),
        price=merged_data.get("price"),
        barcode=merged_data.get("barcode")
    )

    product_dict.update(validated_product.to_dict())
    return jsonify(product_dict), 200

@app.route("/inventory/<int:id>", methods=["DELETE"])
def delete_product(id):
    global inventory
    product = next((p for p in inventory if p["id"] == id), None)
    if not product:
        return jsonify({"message": "Inventory item not found"}), 404
    inventory = [p for p in inventory if p["id"] != id]
    return jsonify({"message": "Inventory item deleted"}), 200

@app.route("/inventory/lookup", methods=["GET"])
def lookup_product():
    barcode = request.args.get("barcode")
    name = request.args.get("name")

    if barcode:
        result = fetch_by_barcode(barcode)
        if result == "server unavailable":
            return jsonify({"message": "Unable to perform request at this time. Please try again later."}), 502
        if not result:
            return jsonify({"message": "Product not found"}), 404
        return jsonify(result), 200
    elif name:
        result = fetch_by_name(name)
        if result == "server unavailable":
            return jsonify({"message": "Unable to perform request at this time. Please try again later."}), 502
        if not result:
            return jsonify({"message": "Product not found"}), 404
        return jsonify(result), 200
    else:
        return jsonify({"message": "Please provide a barcode or name"}), 400

if __name__ == "__main__":
    app.run(debug=True, port=5555)