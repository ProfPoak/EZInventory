from flask import Flask, jsonify, request
from db.db import inventory
from classes.Product import Product

app = Flask(__name__)

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

if __name__ == "__main__":
    app.run(debug=True, port=5555)