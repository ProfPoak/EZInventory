from flask import Flask, jsonify, request
from db.db import inventory

app = Flask(__name__)

@app.route("/inventory", methods=["GET"])
def get_inventory():
    return jsonify(inventory), 200

@app.route("/inventory/<int:id>", methods=["GET"])
def get_inventory_by_id(id):
    for i in inventory:
        if i["id"] == id:
            return jsonify(i), 200
    return jsonify({"message": "inventory item does not exist"}), 404



if __name__ == "__main__":
    app.run(debug=True, port=5555)