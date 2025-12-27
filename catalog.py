from product import Product
from DB2 import ProductDAL


class Catalog:
    def __init__(self):
        # יצירת מופע של ה-DAL
        self.product_dal = ProductDAL()

    def __str__(self):
        # קורא את כל המוצרים הפעילים מה-DB להדפסה
        active_products = self.product_dal.get_all_products()
        return "\n".join(str(p) for p in active_products)

    def __repr__(self):
        return self.__str__()

    def add_product(self, product):
        if not isinstance(product, Product):
            raise TypeError("object needs to be a Product")

        # ⚠️ בדיקה האם המוצר כבר קיים ב-DB באמצעות ה-DAL
        if self.product_dal.get_product_by_id(product.product_id):
            raise ValueError("product already exist")

        # ⚠️ שמירת המוצר ב-DB באמצעות ה-DAL
        self.product_dal.add_product(product)
        return True  # נהוג להחזיר הצלחה

    def get_by_id(self, product_id):
        # ⚠️ שליפה ישירה מה-DB באמצעות ה-DAL
        return self.product_dal.get_product_by_id(product_id)

    def get_by_name(self, name, size=None):
        # ⚠️ כאן עדיין נדרש קוד לוגיקה, כי ה-DAL לא תמיד יודע לסנן לפי שם/גודל
        # (נדרשת פונקציה חדשה ב-DAL, או קריאת כל הנתונים וסינון בפייתון)
        # נשלוף את כולם ונמיין בזיכרון:
        all_products = self.product_dal.get_all_products()
        for p in all_products:
            if p.name == name:
                if name == "בטטה":
                    if p.size == size:
                        return p
                else:
                    return p
        return None

    def list_all(self):
        # ⚠️ שליפת כל הפריטים (אנו מניחים שה-DAL מחזיר רק פעילים)
        return self.product_dal.get_all_products()

    def list_active(self):
        # ⚠️ בהנחה שה-DAL מחזיר רק פריטים פעילים כברירת מחדל:
        return self.product_dal.get_all_products()