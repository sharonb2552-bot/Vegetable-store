class Product:

    def __init__(self, product_id, name, price, size=None, unit = "ק״ג", active=True, created_at=None):

        self.product_id = str(product_id) if product_id is not None else None
        self.name = name
        self.price = float(price)
        self.size = size
        self.unit = unit
        self.active = bool(active)
        self.created_at = created_at

        if self.name == "בטטה":
            if size not in ["M", "L", "XL"]:
                raise ValueError("add size")
            self.size = size

    def __str__(self):
        if self.size:
            return f"{self.product_id} - {self.name} ({self.size}), {self.price}, per{self.unit},  active={self.active}"
        return f"{self.product_id} - {self.name}, {self.price}, active={self.active}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (isinstance(other, Product)
                and super().__eq__(other)
                and self.product_id == other.product_id)

    def __hash__(self):
        return hash((super().__hash__(), self.product_id, self.name, self.price, self.size, self.active))
