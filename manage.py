import uuid
from datetime import datetime

from DB2 import ProductDAL, CustomerDAL, OrderDAL
from catalog import Catalog
from order import Order


class Manage:
    def __init__(self):
        self.product_dal = ProductDAL()
        self.customer_dal = CustomerDAL()
        self.order_dal = OrderDAL()
        self.catalog = Catalog()

    def __str__(self):
        try:
            # 1. ספירת לקוחות מה-DB (נדרשת מתודת get_count ב-CustomerDAL)
            num_customers = self.customer_dal.get_count()
        except:
            num_customers = "N/A (DB Error)"

        try:
            # 2. ספירת הזמנות מה-DB (נדרשת מתודת get_count ב-OrderDAL)
            num_orders = self.order_dal.count_order()
        except:
            num_orders = "N/A (DB Error)"

            # 3. נשתמש ב-__str__ של Catalog כדי לקבל את רשימת המוצרים הפעילה
        return (f"Store: Products=\n{self.catalog},"
                f"\nCustomers={num_customers} in DB,"
                f"\nOrders={num_orders} in DB")

    def __repr__(self):
        return self.__str__()

    def add_customer(self, customer):
        if self.get_customer(customer.customer_id) is not None:
            raise ValueError("This customer already exist")

        self.customer_dal.add_customer(customer)

        return True

    def get_customer(self, customer_id):
        return self.customer_dal.get_customer_by_id(customer_id)

    def create_order(self, customer_id, name, created_at=None):
        # בדיקת קיום לקוח ב-DB באמצעות ה-DAL
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer does not exist")

        # יצירת ID בפורמט: ORDER_YYYYMMDD_XXXX
        date_str = datetime.now().strftime("%Y%m%d")
        unique_part = str(uuid.uuid4())[:8].upper()
        order_id = f"ORD_{date_str}_{unique_part}"

        # יצירת אובייקט Order חדש בזיכרון
        order = Order(order_id, customer_id, name, created_at, status="NEW")

        return order

    def get_order(self, order_id):
        # קורא ישירות מה-DB באמצעות ה-DAL (משתמש במתודה המורכבת עם JOIN)
        return self.order_dal.get_order_by_id(order_id)

    def add_item_to_order(self, order_id, product_id, qty, unit_price=None):
        # בדיקה אם ההזמנה קיימת (שליפה מה-DB)
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("Order not found")

        # שליפת המוצר (שליפה מה-DB)
        product = self.catalog.get_by_id(product_id)
        if product is None:
            raise ValueError("Product not found")

        # בדיקות לוגיקה עסקיות
        if not product.active:
            raise ValueError("Inactive product")
        if order.status != "NEW":
            raise ValueError("cannot add items to a non-NEW order")
        if qty <= 0:
            raise ValueError("Quantity must be positive num")

        # הוספה לאובייקט Order בזיכרון
        order.add_item(product, qty, unit_price)

        # ⚠️ הערה: השמירה ל-DB תתבצע במתודת complete_order

        return True

    def complete_order(self, order_id):
        # 1. שליפת ההזמנה מה-DB (משתמש ב-get_order המתוקנת)
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("order not found")

        # 2. בדיקות סטטוס ולוגיקה עסקית (נשארות כמות שהן)
        if order.status == "CANCELED":
            raise ValueError("Cannot complete a canceled order")
        if order.status == "COMPLETED":
            raise ValueError("Order already completed")

        # 3. שינוי סטטוס האובייקט בזיכרון
        order.complete()

        # 4. ⚠️ שמירת ההזמנה ופריטיה ב-DB (הטרנזקציה המרכזית)
        # זה מעדכן את טבלאות Orders ו-order_items
        saved_order_id = self.order_dal.create_order(order)

        # אם הטרנזקציה נכשלה, יוצאים
        if saved_order_id is None:
            raise Exception("Failed to save order transaction to DB.")

        # 5. עדכון חוב הלקוח (נשאר בזיכרון בינתיים לצורך חישוב)
        customer = self.get_customer(order.customer_id)
        if customer is None:
            raise ValueError("customer not found")

        # חישוב היתרה החדשה: היתרה הקיימת ב-DB + סכום ההזמנה החדשה
        new_balance = customer.balance + order.total_amount

        # 6. ⚠️ שמירת היתרה החדשה ב-DB באמצעות ה-DAL
        self.customer_dal.update_balance(customer.customer_id, new_balance)

        # 7. ⚠️ נמחק את שורת הזיכרון: customer.current_balance += order.total_amount

        return True

    def cancel_order(self, order_id):
        # שליפת ההזמנה (שליפה מה-DB)
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("Order not found")

        # בדיקת לוגיקה עסקית
        if order.status == "COMPLETED":
            raise ValueError("cannot cancel a completed order")

        # 1. שינוי הסטטוס באובייקט הזיכרון
        order.cancel()

        # 2. ⚠️ שמירת הסטטוס המעודכן ב-DB באמצעות ה-DAL
        self.order_dal.update_order_status(order_id, order.status)

        # ⚠️ (השורה המקורית: order.cancel() ו-return True נשארו)
        return True

    def get_prod_by_id(self, product_id):
        return self.catalog.get_by_id(product_id)

    def add_payment(self, customer_id, amount):
        # 1. שליפת הלקוח (שליפה מה-DB)
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")

        # 2. בדיקות לוגיקה עסקיות (נשארות כמות שהן)
        if amount <= 0:
            raise ValueError("Payment amount must be positive")

        # ⚠️ שימו לב: נניח שהמאזן נקרא customer.balance (או customer.current_balance)
        if amount > customer.balance:  # משתמש ב-balance, הנחתי שזה השם הנכון לאחר תיקון
            raise ValueError("Debt cant be negative")

        # 3. חישוב היתרה החדשה בזיכרון (הפחתה מהחוב)
        new_balance = customer.balance - amount

        # 4. ⚠️ שמירת היתרה החדשה ב-DB באמצעות ה-DAL
        self.customer_dal.update_balance(customer_id, new_balance)

        # 5. עדכון אובייקט הזיכרון (אופציונלי, למקרה שהלקוח נשמר בזיכרון)
        customer.balance = new_balance

        return True

    def get_customer_balance(self, customer_id):
        customer = self.get_customer(customer_id)
        if customer is None:
            raise ValueError("Customer not found")

        return customer.balance

    def update_item_qty(self, order_id: str, product_id: str, new_qty: int) -> bool:
        # שליפת ההזמנה מה-DB (שליפה לזיכרון)
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.status != "NEW":
            raise ValueError("Cannot modify items on non-NEW order")
        if new_qty <= 0:
            raise ValueError("Quantity must be positive")

        # 1. חיפוש הפריט ועדכון בזיכרון
        found = False
        new_items = []

        # 2. איפוס הסכום הכולל (נחשב אותו מחדש)
        new_total = 0.0

        # הלולאה עוברת על הפריטים הנוכחיים
        for (pid, name, qty, unit_price, line_total) in order.items:

            current_pid = pid  # משתנה עזר להבנת הקוד

            if current_pid == product_id:
                # עדכון הכמות וחישוב מחדש של סכום השורה
                updated_line_total = float(unit_price) * new_qty
                found = True

                # יצירת טאפל הפריט המעודכן (כדי להתאים למבנה self.items)
                new_items.append((pid, name, new_qty, unit_price, updated_line_total))
                new_total += updated_line_total  # הוספת הסכום המעודכן
            else:
                # הוספת פריטים אחרים כפי שהם
                new_items.append((pid, name, qty, unit_price, line_total))
                new_total += line_total  # הוספת הסכום הקיים

        if not found:
            raise ValueError("Item not found in order")

        # 3. החלפת רשימת הפריטים ועדכון סכום ההזמנה
        order.items = new_items
        order.total_amount = new_total

        # ⚠️ הערה: השמירה ל-DB תתבצע רק ב-complete_order.
        return True

    def remove_item_from_order(self, order_id: str, product_id: str) -> bool:
        # שליפת ההזמנה מה-DB (שליפה לזיכרון)
        order = self.get_order(order_id)
        if order is None:
            raise ValueError("Order not found")
        if order.status != "NEW":
            raise ValueError("Cannot modify items on non-NEW order")

        new_items = []
        new_total = 0.0  # ⚠️ אתחול נכון של סכום חדש
        removed = False

        # 1. לולאה על הפריטים הקיימים
        for (pid, name, qty, unit_price, line_total) in order.items:

            if pid == product_id:
                removed = True
                continue  # ⚠️ אם זה הפריט להסרה, מדלגים עליו

            # 2. ✅ הוספת הפריט לרשימה החדשה וחישוב הסכום הכולל
            new_items.append((pid, name, qty, unit_price, line_total))
            new_total += line_total  # ⚠️ חישוב הסכום המצטבר הנכון

        if not removed:
            raise ValueError("Item not found in order")

        # 3. החלפת רשימת הפריטים ועדכון סכום ההזמנה
        order.items = new_items
        order.total_amount = new_total  # ⚠️ עדכון ה-total_amount של האובייקט

        # ⚠️ (השמירה ל-DB תתבצע רק ב-complete_order)
        return True
