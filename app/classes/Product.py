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
    
    @property
    def product_name(self):
        return self._product_name
    
    @product_name.setter
    def product_name(self, value):
        if not isinstance(value, str):
            raise TypeError("Product name must be a string")
        self._product_name = value

    @property
    def brands(self):
        return self._brands

    @brands.setter
    def brands(self, value):
        if not isinstance(value, str):
            raise TypeError("Brands must be a string")
        self._brands = value

    @property
    def ingredients_text(self):
        return self._ingredients_text

    @ingredients_text.setter
    def ingredients_text(self, value):
        if not isinstance(value, str):
            raise TypeError("Ingredients text must be a string")
        self._ingredients_text = value

    @property
    def quantity(self):
        return self._quantity

    @quantity.setter
    def quantity(self, value):
        if not isinstance(value, str):
            raise TypeError("Quantity must be a string")
        self._quantity = value

    @property
    def stock(self):
        return self._stock
    
    @stock.setter
    def stock(self, value):
        if not isinstance(value, int):
            raise TypeError("Stock must be an integer")
        if value <= 0:
            raise ValueError("Stock must be a positive integer")
        self._stock = value

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError("Price must be a number")
        if value <= 0:
            raise ValueError("Price must be a positive number")
        self._price = value

    @property
    def barcode(self):
        return self._barcode
    
    @barcode.setter
    def barcode(self, value):
        if value is None or isinstance(value, bool):
            raise TypeError("Barcode must be a numeric string with no symbols")
        str_value = str(value)
        if not str_value.isdecimal():
            raise TypeError("Barcode must be a numeric string with no symbols")
        self._barcode = str_value
