class Product:
    def __init__(self, id, product_name, brands, ingredients_text, quantity, stock, price, barcode):
        self.id = id
        self.product_name = product_name
        self.brands = brands
        self.ingredients_text = ingredients_text
        self.quantity = quantity
        self.stock = stock
        self.price = price
        self.barcode = barcode

    def to_dict(self):
        return {
            "id": self.id,
            "product_name": self.product_name,
            "brands": self.brands,
            "ingredients_text": self.ingredients_text,
            "quantity": self.quantity,
            "stock": self.stock,
            "price": self.price,
            "barcode": self.barcode
        }