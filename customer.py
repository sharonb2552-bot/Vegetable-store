class Customer:

    def __init__(self, customer_id, name, phone=None, address=None, email=None, balance=0,customer_type='retail', created_at=None):
        self.customer_id = customer_id
        self.name = name
        self.phone = phone
        self.address = address
        self.email = email
        self.balance = float(balance)
        self.customer_type = customer_type
        self.created_at = created_at
        self.orders = []

    def __str__(self):
        return f"{self.customer_id} - {self.name}, balance={self.balance}, order history={len(self.orders)} orders"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        return (isinstance(other, Customer)
                and self.customer_id == other.customer_id)

    @property
    def current_balance(self):
        return self.balance

    def add_payment(self, amount):
        if amount <= 0:
            raise ValueError("must be positive number")

        if amount > self.balance:
            raise ValueError("Debt cant be negative")

        self.balance -= amount
        return True

    def add_order(self, order):
        self.orders.append(order)

    def get_debt(self):
        return self.balance
    

