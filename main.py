
from manage import Manage
from product import Product
from customer import Customer

def demo():
    # 1) יוצרים את ה"חנות" (Store)
    store = Manage()

    # 2) מוסיפים מוצרים לקטלוג
    store.catalog.add_product(Product("P001", "תפוח אדמה לבן", 3.5))
    store.catalog.add_product(Product("P002", "תפוח אדמה אדום", 4.0))
    store.catalog.add_product(Product("P003", "גזר", 2.2, active=False))
    store.catalog.add_product(Product("P004", "אבטיח", 10.0))
    store.catalog.add_product(Product("P005", "בטטה", 4.5, size="M"))
    store.catalog.add_product(Product("P006", "בטטה", 5.5, size="L"))
    store.catalog.add_product(Product("P007", "בטטה", 6.5, size="XL"))

    print("=== קטלוג מוצרים ===")
    print(store.catalog)
    print()

    # 3) מוסיפים לקוח
    customer = Customer(customer_id="C001", name="דני")
    store.add_customer(customer)
    print("=== לקוחות ===")
    for c in store.customers:
        print(c)
    print()

    order = store.create_order(customer_id="C001", name="דני")
    print("נוצרה הזמנה:", order)

    # נסמן מוצר לא פעיל (למשל גזר P003)
    p = store.catalog.get_by_id("P003")
    p.active = False
    print(f"\nכיביתי את המוצר: {p}")

    # 5) ננסה להוסיף את המוצר הלא-פעיל להזמנה
    try:
        store.add_item_to_order(order_id=order.order_id, product_id="P003", qty=5)
    except ValueError as e:
        print("נתפסה שגיאה כצפוי:", e)

    # כדי להראות שהכול תקין עם מוצר פעיל — נוסיף מוצר פעיל
    store.add_item_to_order(order_id=order.order_id, product_id="P005", qty=2)  # בטטה (M)
    print("\nפריטים אחרי ניסיון כושל + הוספה תקינה:")
    print("פריטים בהזמנה:", order.get_items())
    print("סכום כולל:", order.get_total())

    print("\n>>> לפני תשלום, חוב:", store.get_customer_balance("C001"))
    store.add_payment("C001", 5.0)
    print(">>> אחרי תשלום 5.0, חוב:", store.get_customer_balance("C001"))
if __name__ == "__main__":
    demo()