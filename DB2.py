import mysql.connector
from customer import Customer
from product import Product
from order import Order

# --- הגדרות ---
DB_PASSWORD = '159753'
DB_CONFIG = {
    'user': 'storedb1',  # ✅ תוקן מ-username ל-user
    'password': DB_PASSWORD,
    'host': 'localhost',
    'database': 'storedb1'
}


def get_db_connection():
    """
    יוצר חיבור חדש למסד הנתונים.
    משתמש ב-DB_CONFIG הקבוע.
    """
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        raise ConnectionError(f"שגיאה בחיבור ל-MySQL: {err}")


class CustomerDAL:
    """שכבת גישה לנתונים עבור לקוחות (Customers)."""

    def add_customer(self, customer: Customer):
        """מוסיפה לקוח חדש ל-DB ומחזירה את ה-ID שלו."""
        sql = """
            INSERT INTO Customers (customer_id, name, phone, address, email, balance)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        data = (customer.customer_id, customer.name, customer.phone,
                customer.address, customer.email, customer.balance)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            print(f"✅ Customer '{customer.name}' added successfully.")
            return True
        except Exception as e:
            print(f"❌ Error adding customer: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_customer_by_id(self, customer_id: str):
        """שולף לקוח בודד לפי ID."""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT customer_id, name, phone, address, email, balance, created_at 
                FROM Customers 
                WHERE customer_id = %s
            """, (customer_id,))

            row = cursor.fetchone()
            if row:
                return Customer(**row)
            return None
        except Exception as e:
            print(f"❌ Error reading customer: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_balance(self, customer_id: str, new_balance: float):
        """מעדכן את שדה balance של הלקוח ב-DB."""
        sql = "UPDATE Customers SET balance = %s WHERE customer_id = %s"
        data = (new_balance, customer_id)

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                conn.commit()
                return True
        except Exception as e:
            print(f"❌ Error updating customer balance: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_customer(self, customer: Customer):
        """מעדכן את כל פרטי הלקוח ב-DB."""
        sql = """
            UPDATE Customers 
            SET name = %s, phone = %s, address = %s, email = %s, balance = %s
            WHERE customer_id = %s
        """
        data = (customer.name, customer.phone, customer.address,
                customer.email, customer.balance, customer.customer_id)

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error updating customer: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def delete_customer(self, customer_id: str):
        """מוחק לקוח מה-DB (רק אם אין לו הזמנות)."""
        sql = "DELETE FROM Customers WHERE customer_id = %s"

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (customer_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error deleting customer: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_count(self):
        """סופר את מספר הלקוחות בטבלה."""
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Customers")
                return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_all_customers(self):
        """שולפת את כל הלקוחות מה-DB ומחזירה אותם כרשימת אובייקטי Customer."""
        customers = []
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT customer_id, name, phone, address, email, balance, created_at 
                FROM Customers
            """)

            for row in cursor.fetchall():
                customer = Customer(**row)
                customers.append(customer)

            return customers
        except Exception as e:
            print(f"❌ שגיאה בשליפת לקוחות: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()


class ProductDAL:
    """שכבת גישה לנתונים עבור מוצרים (Products)."""

    def add_product(self, product: Product):
        """מוסיפה מוצר חדש לטבלת Products."""
        sql = """
            INSERT INTO Products (product_id, name, price, size, active)
            VALUES (%s, %s, %s, %s, %s)
        """
        data = (product.product_id, product.name, product.price,
                product.size, product.active)

        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute(sql, data)
            conn.commit()
            print(f"✅ Product '{product.name}' added to DB successfully.")
            return True
        except Exception as e:
            print(f"❌ Error adding product to DB: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_product(self, product: Product):
        """מעדכן מוצר קיים ב-DB."""
        sql = """
            UPDATE Products 
            SET name = %s, price = %s, size = %s, active = %s
            WHERE product_id = %s
        """
        data = (product.name, product.price, product.size,
                product.active, product.product_id)

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, data)
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error updating product: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def deactivate_product(self, product_id: str):
        """מסמן מוצר כלא פעיל (soft delete)."""
        sql = "UPDATE Products SET active = FALSE WHERE product_id = %s"

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (product_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error deactivating product: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_all_products(self):
        """שולפת את כל המוצרים הפעילים ומחזירה כרשימת אובייקטי Product."""
        products = []
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT product_id, name, price, size, active, created_at 
                FROM Products 
                WHERE active = TRUE
            """)

            for row in cursor.fetchall():
                print(f"DEBUG DB row: {row}")
                product = Product(**row)
                print(f"DEBUG Product: {product.name}, size={product.size}")
                products.append(product)

            return products
        except Exception as e:
            print(f"❌ שגיאה בשליפת מוצרים: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_product_by_id(self, product_id: str):
        """שולף מוצר בודד לפי ID."""
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            cursor.execute("""
                SELECT product_id, name, price, size, active, created_at 
                FROM Products 
                WHERE product_id = %s
            """, (product_id,))

            row = cursor.fetchone()
            if row:
                return Product(**row)
            return None
        except Exception as e:
            print(f"❌ Error reading product: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()


class OrderDAL:
    """שכבת גישה לנתונים עבור הזמנות (Orders)."""

    def create_order(self, order: Order):
        """
        יוצר הזמנה חדשה במסד הנתונים.
        מכניס גם את כותרת ההזמנה (Orders) וגם את הפריטים (Order_items).
        משתמש בטרנזקציה כדי להבטיח עקביות.
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor()

            # התחלת טרנזקציה
            conn.start_transaction()

            # 1. הכנסת כותרת ההזמנה
            order_sql = """
                INSERT INTO Orders (order_id, customer_id, status, total)
                VALUES (%s, %s, %s, %s)
            """
            order_data = (order.order_id, order.customer_id,
                          order.status, order.total_amount)
            cursor.execute(order_sql, order_data)

            # 2. הכנסת פריטי ההזמנה
            item_sql = """
                INSERT INTO Order_items (order_id, product_id, qty, unit_price, line_total)
                VALUES (%s, %s, %s, %s, %s)
            """
            for item in order.items:
                # item הוא tuple: (product_id, name, qty, unit_price, line_total)
                item_data = (order.order_id, item[0], item[2], item[3], item[4])
                cursor.execute(item_sql, item_data)

            # אישור הטרנזקציה
            conn.commit()
            print(f"✅ Order '{order.order_id}' created successfully.")
            return True

        except Exception as e:
            if conn:
                conn.rollback()
            print(f"❌ Error creating order: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def update_order_status(self, order_id: str, new_status: str):
        """מעדכן את סטטוס ההזמנה."""
        sql = "UPDATE Orders SET status = %s WHERE order_id = %s"

        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute(sql, (new_status, order_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            print(f"❌ Error updating order status: {e}")
            return False
        finally:
            if conn and conn.is_connected():
                conn.close()

    def count_order(self):
        """סופר את מספר ההזמנות בטבלה."""
        conn = None
        try:
            conn = get_db_connection()
            with conn.cursor() as cursor:
                cursor.execute("SELECT COUNT(*) FROM Orders")
                return cursor.fetchone()[0]
        except Exception:
            return 0
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_order_by_id(self, order_id: str):
        """
        שולף הזמנה (Orders) וכל פריטי ההזמנה (Order_items) הקשורים אליה
        ומחזיר אותם כאובייקט Order.
        """
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # שאילתת SQL עם JOIN לשליפת כל הנתונים משתי הטבלאות
            sql = """
                SELECT 
                    o.order_id, o.customer_id, o.status, o.total, o.created_at, 
                    oi.product_id, oi.qty, oi.unit_price, oi.line_total,
                    p.name as product_name
                FROM Orders o
                LEFT JOIN Order_items oi ON o.order_id = oi.order_id
                LEFT JOIN Products p ON oi.product_id = p.product_id
                WHERE o.order_id = %s
            """
            cursor.execute(sql, (order_id,))
            rows = cursor.fetchall()

            if not rows:
                return None

            # בניית אובייקט Order
            first_row = rows[0]
            order = Order(
                order_id=first_row['order_id'],
                customer_id=first_row['customer_id'],
                customer_name="שם לא ידוע (יש לשלוף בנפרד)",
                created_at=first_row['created_at'],
                status=first_row['status'],
                total_amount=first_row['total']
            )

            # הוספת הפריטים
            order.items = []
            for row in rows:
                if row['product_id']:
                    item_tuple = (
                        row['product_id'],
                        row['product_name'] or "שם לא ידוע",
                        row['qty'],
                        row['unit_price'],
                        row['line_total']
                    )
                    order.items.append(item_tuple)

            return order

        except Exception as e:
            print(f"❌ שגיאה בשליפת הזמנה {order_id}: {e}")
            return None
        finally:
            if conn and conn.is_connected():
                conn.close()

    def get_all_orders(self):
        """שולף את כל ההזמנות מה-DB כולל הפריטים שלהן."""
        orders = []
        conn = None
        try:
            conn = get_db_connection()
            cursor = conn.cursor(dictionary=True)

            # שליפת כל ההזמנות
            cursor.execute("""
                SELECT order_id, customer_id, status, total, created_at
                FROM Orders
                ORDER BY created_at DESC
            """)
            order_rows = cursor.fetchall()

            for row in order_rows:
                order = Order(
                    order_id=row['order_id'],
                    customer_id=row['customer_id'],
                    customer_name="",
                    created_at=row['created_at'],
                    status=row['status'],
                    total_amount=row['total']
                )

                # שליפת הפריטים של ההזמנה
                cursor.execute("""
                    SELECT oi.product_id, p.name as product_name, p.size, oi.qty, oi.unit_price, oi.line_total
                    FROM Order_items oi
                    LEFT JOIN Products p ON oi.product_id = p.product_id
                    WHERE oi.order_id = %s
                """, (row['order_id'],))

                items = cursor.fetchall()
                for item in items:
                    # הוספת הגודל לשם אם קיים
                    if item['size']:
                        product_name = f"{item['product_name']} ({item['size']})"
                    else:
                        product_name = item['product_name'] or "שם לא ידוע"

                    item_tuple = (
                        item['product_id'],
                        product_name,
                        item['qty'],
                        item['unit_price'],
                        item['line_total']
                    )
                    order.items.append(item_tuple)

                orders.append(order)

            return orders
        except Exception as e:
            print(f"❌ שגיאה בשליפת הזמנות: {e}")
            return []
        finally:
            if conn and conn.is_connected():
                conn.close()

if __name__ == '__main__':
    # בדיקה בסיסית
    try:
        print("🔍 בודק חיבור למסד הנתונים...")
        conn = get_db_connection()
        print("✅ החיבור הצליח!")
        conn.close()

        # בדיקת CustomerDAL
        customer_manager = CustomerDAL()
        print(f"📊 מספר לקוחות במערכת: {customer_manager.get_count()}")

        # בדיקת ProductDAL
        product_manager = ProductDAL()
        products = product_manager.get_all_products()
        print(f"📦 מספר מוצרים פעילים: {len(products)}")

        # בדיקת OrderDAL
        order_manager = OrderDAL()
        print(f"🛒 מספר הזמנות במערכת: {order_manager.count_order()}")

    except Exception as e:
        print(f"❌ שגיאה: {e}")
