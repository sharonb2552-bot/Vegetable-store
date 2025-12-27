from product import Product
from catalog import Catalog
from customer import Customer
p1 = Product("P001", "תפוח אדמה לבן", "3.5")
p2 = Product("P002", "בטטה", "4.2", size="M")

print(p1)
print(p2)


cat = Catalog()
print(cat)
cat.add_product(Product("P001", "תפוח אדמה לבן", 3.5))
cat.add_product(Product("P002", "בטטה", 4.2, size="M"))

print(cat)  # תראה שני מוצרים
print()
cat.add_product(Product("P011", "תפוח אדמה אדום", 3.7))
print(cat)


c = Customer("C001", "דני")
c.current_balance = 20.0   # יש חוב

c.add_payment(10)
c.add_payment(15)
