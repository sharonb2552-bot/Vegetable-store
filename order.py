from datetime import datetime



class Order:

    def __init__(self, order_id, customer_id, customer_name, created_at=None, status="NEW", total_amount=0.0):
        self.order_id = order_id
        self.customer_id = customer_id
        self.customer_name = customer_name
        self.created_at = created_at
        self.status = status
        self.items = []
        self.total_amount = total_amount

    def __str__(self):
        return (f"Order({self.order_id}) "
                f"customer=({self.customer_id}, {self.customer_name}) "
                f"status={self.status}) "
                f"items={self.items} "
                f"total={self.total_amount}")

    def add_item(self, product, qty, unit_price=None):
        """
        מוסיף פריט להזמנה. אם המוצר כבר קיים בשורות — מבצע merge:
        מגדיל את הכמות ומחשב מחדש את סכום השורה והסכום הכולל.
        """
        # קבע מחיר יחידה: אם קיבלת מחיר, השתמש בו; אחרת המחיר של המוצר
        price = float(unit_price) if unit_price is not None else float(product.price)

        # ננסה למצוא שורה קיימת של אותו product_id
        found_index = -1
        for idx, (pid, name, old_qty, old_unit_price, old_line_total) in enumerate(self.items):
            if pid == product.product_id:
                found_index = idx
                # אם נשלח unit_price חדש — נעדכן את מחיר היחידה; אחרת נשמור את הקיים
                if unit_price is not None:
                    old_unit_price = price
                new_qty = old_qty + int(qty)
                new_line_total = float(old_unit_price) * new_qty
                # מחליפים את השורה במקום
                self.items[idx] = (pid, name, new_qty, old_unit_price, new_line_total)
                break

        # אם לא נמצאה שורה קיימת — מוסיפים שורה חדשה
        if found_index == -1:
            line_total = price * int(qty)
            self.items.append((
                product.product_id,
                product.name,
                int(qty),
                price,
                float(line_total),
            ))

        # מחשבים מחדש את סכום ההזמנה
        self.total_amount = sum(line_total for (_pid, _name, _q, _price, line_total) in self.items)
        return True

    def get_total(self):
        return self.total_amount

    def get_items(self):
        return self.items

    def remove_item(self, product_name, size=None):
        for i, (p_id, name, qty, price, line_total) in enumerate(self.items):
            if name == product_name:
                if product_name == "בטטה" and size is not None:
                    pass
                self.total_amount -= line_total
                self.items.pop(i)
                return True
            return False

    def complete(self):
        if len(self.items) == 0:
            raise ValueError("must add products")
        if self.status == "CANCELED":
            raise ValueError("Cant complete a canceled order")
        self.status = "COMPLETED"
        return True

    def cancel(self):
        if self.status == "COMPLETED":
            raise ValueError("Cant cancel completed order")
        self.status = "CANCELED"
        return True



