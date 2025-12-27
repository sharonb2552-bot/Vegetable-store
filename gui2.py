# gui_app.py
import tkinter as tk
from tkinter import messagebox, ttk
from manage import Manage
from customer import Customer
from product import Product
from order import Order

# יצירת מופע של מחלקת הלוגיקה
store_manager = Manage()


class StoreApp:
    def __init__(self, master):
        self.master = master
        master.title("ממשק ניהול חנות")
        master.geometry("1000x700")

        # משתנים לשמירת ההזמנה הנוכחית בזיכרון
        self.current_order = None
        self.all_customers = []

        # יצירת Notebook (חלון עם כרטיסיות)
        self.notebook = ttk.Notebook(master)
        self.notebook.pack(expand=True, fill='both', padx=10, pady=10)

        # יצירת כרטיסיות
        self.customer_frame = ttk.Frame(self.notebook)
        self.product_frame = ttk.Frame(self.notebook)
        self.order_frame = ttk.Frame(self.notebook)
        self.order_history_frame = ttk.Frame(self.notebook)
        self.finance_frame = ttk.Frame(self.notebook)

        self.notebook.add(self.customer_frame, text='ניהול לקוחות')
        self.notebook.add(self.product_frame, text='ניהול מוצרים')
        self.notebook.add(self.order_frame, text='יצירת הזמנה')
        self.notebook.add(self.order_history_frame, text='היסטוריית הזמנות')
        self.notebook.add(self.finance_frame, text='ניהול כספים')

        # הגדרת הרכיבים
        self._setup_customer_widgets(self.customer_frame)
        self._setup_product_widgets(self.product_frame)
        self._setup_order_widgets(self.order_frame)
        self._setup_order_history_widgets(self.order_history_frame)
        self._setup_finance_widgets(self.finance_frame)

        # טעינת נתונים ראשונית
        self.load_products()
        self.load_customers()
        self.load_customers_list()
        self.load_products_list()
        self.load_order_history()

    # ============================================
    # ניהול לקוחות
    # ============================================
    def _setup_customer_widgets(self, frame):
        # פאנל הוספת לקוח
        add_panel = ttk.LabelFrame(frame, text="הוספת לקוח חדש")
        add_panel.pack(padx=10, pady=10, fill='x')

        tk.Label(add_panel, text="ID לקוח:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.cust_id_entry = tk.Entry(add_panel, width=20)
        self.cust_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_panel, text="שם:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.cust_name_entry = tk.Entry(add_panel, width=30)
        self.cust_name_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(add_panel, text="טלפון:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.cust_phone_entry = tk.Entry(add_panel, width=20)
        self.cust_phone_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_panel, text="כתובת:").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.cust_address_entry = tk.Entry(add_panel, width=30)
        self.cust_address_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Label(add_panel, text="אימייל:").grid(row=2, column=0, padx=5, pady=5, sticky='e')
        self.cust_email_entry = tk.Entry(add_panel, width=20)
        self.cust_email_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(add_panel, text="הוסף לקוח", command=self.add_customer_handler,
                  bg="green", fg="white").grid(row=2, column=3, padx=5, pady=5)

        # טבלת לקוחות
        list_panel = ttk.LabelFrame(frame, text="רשימת לקוחות")
        list_panel.pack(padx=10, pady=10, fill='both', expand=True)

        self.customers_tree = ttk.Treeview(list_panel,
                                           columns=('ID', 'שם', 'טלפון', 'כתובת', 'אימייל', 'חוב'),
                                           show='headings')
        for col in ('ID', 'שם', 'טלפון', 'כתובת', 'אימייל', 'חוב'):
            self.customers_tree.heading(col, text=col)
            self.customers_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(list_panel, orient='vertical', command=self.customers_tree.yview)
        self.customers_tree.configure(yscrollcommand=scrollbar.set)
        self.customers_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        tk.Button(frame, text="רענן רשימה", command=self.load_customers).pack(pady=5)

    def add_customer_handler(self):
        cust_id = self.cust_id_entry.get().strip()
        name = self.cust_name_entry.get().strip()
        phone = self.cust_phone_entry.get().strip()
        address = self.cust_address_entry.get().strip()
        email = self.cust_email_entry.get().strip()

        if not cust_id or not name:
            messagebox.showwarning("שגיאה", "חובה למלא ID ושם לקוח")
            return

        try:
            customer = Customer(
                customer_id=cust_id,
                name=name,
                phone=phone if phone else None,
                address=address if address else None,
                email=email if email else None
            )
            store_manager.add_customer(customer)
            messagebox.showinfo("הצלחה", f"✅ לקוח {name} נוסף בהצלחה!")

            # ניקוי שדות
            self.cust_id_entry.delete(0, tk.END)
            self.cust_name_entry.delete(0, tk.END)
            self.cust_phone_entry.delete(0, tk.END)
            self.cust_address_entry.delete(0, tk.END)
            self.cust_email_entry.delete(0, tk.END)

            # רענון רשימה
            self.load_customers()
            self.load_customers_list()
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ שגיאה בהוספת לקוח: {e}")

    def load_customers(self):
        """טוען את כל הלקוחות לטבלה"""
        for item in self.customers_tree.get_children():
            self.customers_tree.delete(item)

        try:
            customers = store_manager.customer_dal.get_all_customers()
            for c in customers:
                self.customers_tree.insert('', tk.END, values=(
                    c.customer_id,
                    c.name,
                    c.phone or '',
                    c.address or '',
                    c.email or '',
                    f"{c.balance:.2f}"
                ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בטעינת לקוחות: {e}")

    # ============================================
    # ניהול מוצרים
    # ============================================
    def _setup_product_widgets(self, frame):
        # פאנל הוספת מוצר
        add_panel = ttk.LabelFrame(frame, text="הוספת מוצר חדש")
        add_panel.pack(padx=10, pady=10, fill='x')

        tk.Label(add_panel, text="ID מוצר:").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.prod_id_entry = tk.Entry(add_panel, width=15)
        self.prod_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(add_panel, text="שם:").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.prod_name_entry = tk.Entry(add_panel, width=30)
        self.prod_name_entry.grid(row=0, column=3, padx=5, pady=5)

        tk.Label(add_panel, text="מחיר:").grid(row=1, column=0, padx=5, pady=5, sticky='e')
        self.prod_price_entry = tk.Entry(add_panel, width=15)
        self.prod_price_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(add_panel, text="גודל (אופציונלי):").grid(row=1, column=2, padx=5, pady=5, sticky='e')
        self.prod_size_entry = tk.Entry(add_panel, width=15)
        self.prod_size_entry.grid(row=1, column=3, padx=5, pady=5)

        tk.Button(add_panel, text="הוסף מוצר", command=self.add_product_handler,
                  bg="blue", fg="white").grid(row=2, column=3, padx=5, pady=5)

        # טבלת מוצרים
        list_panel = ttk.LabelFrame(frame, text="רשימת מוצרים")
        list_panel.pack(padx=10, pady=10, fill='both', expand=True)

        self.products_tree = ttk.Treeview(list_panel,
                                          columns=('ID', 'שם', 'מחיר', 'גודל', 'פעיל'),
                                          show='headings')
        for col in ('ID', 'שם', 'מחיר', 'גודל', 'פעיל'):
            self.products_tree.heading(col, text=col)
            self.products_tree.column(col, width=150)

        scrollbar = ttk.Scrollbar(list_panel, orient='vertical', command=self.products_tree.yview)
        self.products_tree.configure(yscrollcommand=scrollbar.set)
        self.products_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        tk.Button(frame, text="רענן רשימה", command=self.load_products).pack(pady=5)

    def add_product_handler(self):
        prod_id = self.prod_id_entry.get().strip()
        name = self.prod_name_entry.get().strip()
        price_str = self.prod_price_entry.get().strip()
        size = self.prod_size_entry.get().strip()

        if not prod_id or not name or not price_str:
            messagebox.showwarning("שגיאה", "חובה למלא ID, שם ומחיר")
            return

        try:
            price = float(price_str)
            product = Product(
                product_id=prod_id,
                name=name,
                price=price,
                size=size if size else None
            )
            store_manager.catalog.add_product(product)
            messagebox.showinfo("הצלחה", f"✅ מוצר {name} נוסף בהצלחה!")

            # ניקוי שדות
            self.prod_id_entry.delete(0, tk.END)
            self.prod_name_entry.delete(0, tk.END)
            self.prod_price_entry.delete(0, tk.END)
            self.prod_size_entry.delete(0, tk.END)

            # רענון רשימה
            self.load_products()
            self.load_products_list()
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ שגיאה בהוספת מוצר: {e}")

    def load_products(self):
        """טוען את כל המוצרים לטבלה"""
        for item in self.products_tree.get_children():
            self.products_tree.delete(item)

        try:
            products = store_manager.catalog.list_all()
            print(f"DEBUG: נטענו {len(products)} מוצרים")  # הוסף שורה זו
            for p in products:
                print(f"DEBUG: {p.product_id}, {p.name}")  # הוסף שורה זו
                self.products_tree.insert('', tk.END, values=(
                    p.product_id,
                    p.name,
                    f"{p.price:.2f}",
                    p.size or '',
                    'כן' if p.active else 'לא'
                ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בטעינת מוצרים: {e}")
    def load_products_list(self):
        """טוען את רשימת המוצרים ל-ComboBox"""
        try:
            products = store_manager.catalog.list_all()
            active_products = [p for p in products if p.active]
            product_options = []
            for p in active_products:
                unit_text = f"ל{p.unit}" if hasattr(p, 'unit') and p.unit else ""
                if p.size:
                    product_options.append(f"{p.product_id} - {p.name} {p.size} - {p.price:.2f} {unit_text}")
                else:
                    product_options.append(f"{p.product_id} - {p.name} - {p.price:.2f} {unit_text}")
            self.product_combo['values'] = product_options
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בטעינת מוצרים: {e}")
    # ============================================
    # יצירת הזמנה
    # ============================================
    def _setup_order_widgets(self, frame):
        frame.columnconfigure(0, weight=1)
        frame.columnconfigure(1, weight=1)

        # 1. בחירת לקוח
        customer_panel = ttk.LabelFrame(frame, text="1. בחירת לקוח")
        customer_panel.grid(row=0, column=0, padx=5, pady=5, sticky='ew', columnspan=2)

        tk.Label(customer_panel, text="בחר לקוח:").pack(side=tk.LEFT, padx=5, pady=5)
        self.customer_var = tk.StringVar()
        self.customer_combo = ttk.Combobox(customer_panel, textvariable=self.customer_var, state="readonly")
        self.customer_combo.pack(side=tk.LEFT, padx=5, pady=5, fill='x', expand=True)
        self.customer_combo.bind('<<ComboboxSelected>>', self.start_new_order)

        self.order_status_label = tk.Label(customer_panel, text="סטטוס: אין הזמנה פעילה", fg="orange")
        self.order_status_label.pack(side=tk.RIGHT, padx=5, pady=5)

        # 2. הוספת פריטים
        items_panel = ttk.LabelFrame(frame, text="2. הוספת פריטים")
        items_panel.grid(row=1, column=0, padx=5, pady=5, sticky='ew', columnspan=2)

        tk.Label(items_panel, text="בחר מוצר:").pack(side=tk.LEFT, padx=5)

        self.product_var = tk.StringVar()
        self.product_combo = ttk.Combobox(items_panel, textvariable=self.product_var, state="readonly", width=50)
        self.product_combo.pack(side=tk.LEFT, padx=5)

        tk.Label(items_panel, text="כמות:").pack(side=tk.LEFT, padx=5)
        self.item_qty_entry = tk.Entry(items_panel, width=10)
        self.item_qty_entry.pack(side=tk.LEFT, padx=5)
        self.item_qty_entry.insert(0, "1")

        tk.Button(items_panel, text="הוסף פריט", command=self.add_item_handler).pack(side=tk.LEFT, padx=10)

        # 3. הצגת פריטי הזמנה
        display_panel = ttk.LabelFrame(frame, text="3. פירוט הזמנה")
        display_panel.grid(row=2, column=0, padx=5, pady=5, sticky='nsew', columnspan=2)
        frame.rowconfigure(2, weight=1)

        self.order_items_tree = ttk.Treeview(display_panel,
                                             columns=('ID', 'שם', 'כמות', 'מחיר יחידה', 'סה"כ שורה'),
                                             show='headings')
        for col in ('ID', 'שם', 'כמות', 'מחיר יחידה', 'סה"כ שורה'):
            self.order_items_tree.heading(col, text=col)
        self.order_items_tree.pack(fill='both', expand=True)

        # סכום כולל
        self.total_label = tk.Label(frame, text="סכום כולל: 0.00 ש''ח",
                                    font=("Arial", 14, "bold"), fg="dark green")
        self.total_label.grid(row=3, column=0, padx=5, pady=10, sticky='w')

        # כפתור סיום
        tk.Button(frame, text="4. בצע הזמנה (שמור ל-DB)",
                  font=("Arial", 12, "bold"), fg="white", bg="green",
                  command=self.complete_order_handler).grid(row=3, column=1, padx=5, pady=10, sticky='e')

    def load_customers_list(self):
        """טוען את רשימת הלקוחות ל-ComboBox"""
        try:
            self.all_customers = store_manager.customer_dal.get_all_customers()
            customer_options = [f"{c.customer_id} - {c.name}" for c in self.all_customers]
            self.customer_combo['values'] = customer_options
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בטעינת לקוחות: {e}")

    def start_new_order(self, event=None):
        """מתחיל הזמנה חדשה"""
        selected = self.customer_var.get()
        if not selected:
            return

        cust_id = selected.split(' - ')[0]
        cust_name = selected.split(' - ')[1]

        try:
            self.current_order = store_manager.create_order(customer_id=cust_id, name=cust_name)
            self.order_status_label.config(text=f"סטטוס: הזמנה חדשה ל-{cust_name}", fg="blue")
            self.refresh_order_display()
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל ביצירת הזמנה: {e}")

    def add_item_handler(self):
        """מוסיף פריט להזמנה"""
        if self.current_order is None:
            messagebox.showwarning("שגיאה", "אנא בחר לקוח כדי להתחיל הזמנה חדשה")
            return

        selected_product = self.product_var.get()
        qty_str = self.item_qty_entry.get().strip()

        if not selected_product or not qty_str:
            messagebox.showwarning("שגיאה", "חובה לבחור מוצר ולהזין כמות")
            return

        try:
            qty = float(qty_str)

            # שליפת ה-ID מהבחירה (עכשיו ה-ID בסוף)
            prod_id = selected_product.split(' - ')[0]

            # שליפת המוצר
            product = store_manager.catalog.get_by_id(prod_id)
            if product is None:
                raise ValueError(f"מוצר {prod_id} לא נמצא")
            if not product.active:
                raise ValueError(f"מוצר {product.name} לא פעיל")
            if qty <= 0:
                raise ValueError("כמות חייבת להיות חיובית")

            # הוספה ישירות לאובייקט ההזמנה בזיכרון
            self.current_order.add_item(product, qty)
            messagebox.showinfo("הצלחה", f"✅ נוסף {product.name} x{qty}")

            self.refresh_order_display()

            # איפוס הבחירה והכמות
            self.product_var.set('')
            self.item_qty_entry.delete(0, tk.END)
            self.item_qty_entry.insert(0, "1")

        except ValueError as e:
            messagebox.showerror("שגיאה", f"❌ {e}")
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ שגיאת מערכת: {e}")
    def refresh_order_display(self):
        """מרענן את תצוגת ההזמנה"""
        for item in self.order_items_tree.get_children():
            self.order_items_tree.delete(item)

        if self.current_order:
            for item in self.current_order.items:
                # שליפת המוצר כדי לקבל את הגודל
                product = store_manager.catalog.get_by_id(item[0])
                if product and product.size:
                    display_name = f"{item[1]} ({product.size})"
                else:
                    display_name = item[1]

                self.order_items_tree.insert('', tk.END,
                                             values=(item[0], display_name, item[2],
                                                     f"{item[3]:.2f}", f"{item[4]:.2f}"))
            total = self.current_order.get_total()
            self.total_label.config(text=f"סכום כולל: {total:.2f} ש''ח")
        else:
            self.total_label.config(text="סכום כולל: 0.00 ש''ח")

    def complete_order_handler(self):
        """מסיים ושומר את ההזמנה"""
        if self.current_order is None or not self.current_order.items:
            messagebox.showwarning("שגיאה", "לא ניתן לבצע הזמנה ריקה")
            return

        try:
            # סימון ההזמנה כ-COMPLETED
            self.current_order.complete()

            # שמירה ל-DB
            store_manager.order_dal.create_order(self.current_order)

            # עדכון חוב הלקוח
            customer = store_manager.get_customer(self.current_order.customer_id)
            if customer:
                new_balance = customer.balance + self.current_order.total_amount
                store_manager.customer_dal.update_balance(customer.customer_id, new_balance)

            messagebox.showinfo("הצלחה",
                                f"✅ הזמנה #{self.current_order.order_id} בוצעה בהצלחה!\n"
                                f"סכום: {self.current_order.total_amount:.2f} ש''ח")

            # איפוס ההזמנה
            self.current_order = None
            self.order_status_label.config(text="סטטוס: הזמנה בוצעה בהצלחה", fg="green")
            self.refresh_order_display()

            # רענון רשימת לקוחות כדי לראות את המאזן המעודכן
            self.load_customers()

            # רענון היסטוריית הזמנות
            self.load_order_history()

        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בביצוע ההזמנה: {e}")

    # ============================================
    # ניהול כספים
    # ============================================
    def _setup_finance_widgets(self, frame):
        # פאנל הוספת תשלום
        payment_panel = ttk.LabelFrame(frame, text="הוספת תשלום")
        payment_panel.pack(padx=10, pady=10, fill='x')

        tk.Label(payment_panel, text="ID לקוח:").pack(side=tk.LEFT, padx=5, pady=5)
        self.pay_id_entry = tk.Entry(payment_panel, width=15)
        self.pay_id_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Label(payment_panel, text="סכום תשלום:").pack(side=tk.LEFT, padx=5, pady=5)
        self.pay_amount_entry = tk.Entry(payment_panel, width=15)
        self.pay_amount_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(payment_panel, text="אשר תשלום", command=self.add_payment_handler).pack(side=tk.LEFT, padx=10)
        self.pay_message_label = tk.Label(payment_panel, text="", fg="blue")
        self.pay_message_label.pack(side=tk.LEFT, padx=5, pady=5)

        # פאנל בדיקת מאזן
        balance_panel = ttk.LabelFrame(frame, text="בדיקת מאזן/חוב")
        balance_panel.pack(padx=10, pady=10, fill='x')

        tk.Label(balance_panel, text="ID לקוח:").pack(side=tk.LEFT, padx=5, pady=5)
        self.balance_id_entry = tk.Entry(balance_panel, width=15)
        self.balance_id_entry.pack(side=tk.LEFT, padx=5, pady=5)

        tk.Button(balance_panel, text="בדוק מאזן", command=self.view_balance_handler).pack(side=tk.LEFT, padx=10)
        self.balance_result_label = tk.Label(balance_panel, text="מאזן: ", font=("Arial", 12))
        self.balance_result_label.pack(side=tk.LEFT, padx=5, pady=5)

    def add_payment_handler(self):
        """מוסיף תשלום"""
        cust_id = self.pay_id_entry.get().strip()
        amount_str = self.pay_amount_entry.get().strip()

        try:
            amount = float(amount_str)
            store_manager.add_payment(cust_id, amount)
            self.pay_message_label.config(text=f"✅ תשלום {amount:.2f} אושר", fg="green")
            self.pay_id_entry.delete(0, tk.END)
            self.pay_amount_entry.delete(0, tk.END)
            self.load_customers()
        except ValueError as e:
            self.pay_message_label.config(text=f"❌ {e}", fg="red")
        except Exception as e:
            self.pay_message_label.config(text=f"❌ שגיאה: {e}", fg="red")

    def view_balance_handler(self):
        """מציג מאזן לקוח"""
        cust_id = self.balance_id_entry.get().strip()

        try:
            balance = store_manager.get_customer_balance(cust_id)
            if balance > 0:
                result_text = f"חוב: {balance:.2f} ש''ח"
                color = "red"
            else:
                result_text = f"יתרה: {abs(balance):.2f} ש''ח"
                color = "blue"
            self.balance_result_label.config(text=f"מאזן {cust_id}: {result_text}", fg=color)
        except ValueError as e:
            self.balance_result_label.config(text=f"❌ {e}", fg="red")
        except Exception as e:
            self.balance_result_label.config(text=f"❌ שגיאה: {e}", fg="red")

    # ============================================
    # היסטוריית הזמנות
    # ============================================
    def _setup_order_history_widgets(self, frame):
        """מגדיר את כרטיסיית היסטוריית ההזמנות"""
        # כותרת ופילטרים
        top_panel = ttk.Frame(frame)
        top_panel.pack(padx=10, pady=10, fill='x')

        tk.Label(top_panel, text="סינון לפי לקוח:", font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        self.order_filter_var = tk.StringVar()
        self.order_filter_combo = ttk.Combobox(top_panel, textvariable=self.order_filter_var,
                                               state="readonly", width=25)
        self.order_filter_combo.pack(side=tk.LEFT, padx=5)
        self.order_filter_combo.bind('<<ComboboxSelected>>', lambda e: self.load_order_history())

        tk.Button(top_panel, text="הצג הכל", command=self.load_all_orders).pack(side=tk.LEFT, padx=5)
        tk.Button(top_panel, text="רענן", command=self.load_order_history,
                  bg="blue", fg="white").pack(side=tk.LEFT, padx=5)

        # טבלת הזמנות
        list_panel = ttk.LabelFrame(frame, text="רשימת הזמנות")
        list_panel.pack(padx=10, pady=10, fill='both', expand=True)

        self.orders_tree = ttk.Treeview(list_panel,
                                        columns=('מס הזמנה', 'לקוח', 'תאריך', 'סטטוס', 'סה"כ', 'פריטים'),
                                        show='headings')
        self.orders_tree.heading('מס הזמנה', text='מס הזמנה')
        self.orders_tree.heading('לקוח', text='לקוח')
        self.orders_tree.heading('תאריך', text='תאריך')
        self.orders_tree.heading('סטטוס', text='סטטוס')
        self.orders_tree.heading('סה"כ', text='סה"כ (₪)')
        self.orders_tree.heading('פריטים', text='פריטים')

        self.orders_tree.column('מס הזמנה', width=150)
        self.orders_tree.column('לקוח', width=150)
        self.orders_tree.column('תאריך', width=150)
        self.orders_tree.column('סטטוס', width=100)
        self.orders_tree.column('סה"כ', width=100)
        self.orders_tree.column('פריטים', width=200)

        scrollbar = ttk.Scrollbar(list_panel, orient='vertical', command=self.orders_tree.yview)
        self.orders_tree.configure(yscrollcommand=scrollbar.set)
        self.orders_tree.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

        # כפתור צפייה בפרטים
        tk.Button(frame, text="צפה בפרטי הזמנה", command=self.view_order_details,
                  font=("Arial", 10, "bold")).pack(pady=5)

    def load_order_history(self):
        """טוען את כל ההזמנות לטבלה"""
        for item in self.orders_tree.get_children():
            self.orders_tree.delete(item)

        try:
            # עדכון רשימת לקוחות לפילטר
            customers = store_manager.customer_dal.get_all_customers()
            customer_options = ["הכל"] + [f"{c.customer_id} - {c.name}" for c in customers]
            self.order_filter_combo['values'] = customer_options
            if not self.order_filter_var.get():
                self.order_filter_var.set("הכל")

            # שליפת הזמנות
            orders = store_manager.order_dal.get_all_orders()

            # סינון לפי לקוח אם נבחר
            selected_filter = self.order_filter_var.get()
            if selected_filter and selected_filter != "הכל":
                filter_customer_id = selected_filter.split(' - ')[0]
                orders = [o for o in orders if o.customer_id == filter_customer_id]

            # הצגת ההזמנות
            for order in orders:
                # שליפת שם הלקוח
                customer = store_manager.get_customer(order.customer_id)
                customer_name = customer.name if customer else "לא ידוע"

                # בניית רשימת פריטים
                items_str = ", ".join([f"{item[1]} x{item[2]}" for item in order.items[:3]])
                if len(order.items) > 3:
                    items_str += "..."

                self.orders_tree.insert('', tk.END, values=(
                    order.order_id,
                    f"{order.customer_id} - {customer_name}",
                    order.created_at.strftime("%d/%m/%Y %H:%M") if order.created_at else "",
                    order.status,
                    f"{order.total_amount:.2f}",
                    items_str if order.items else "אין פריטים"
                ))
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בטעינת הזמנות: {e}")

    def load_all_orders(self):
        """מציג את כל ההזמנות ללא סינון"""
        self.order_filter_var.set("הכל")
        self.load_order_history()

    def view_order_details(self):
        """מציג פרטים מלאים של הזמנה נבחרת"""
        selection = self.orders_tree.selection()
        if not selection:
            messagebox.showwarning("שגיאה", "אנא בחר הזמנה לצפייה")
            return

        item = self.orders_tree.item(selection[0])
        order_id = item['values'][0]

        try:
            order = store_manager.get_order(order_id)
            if not order:
                messagebox.showerror("שגיאה", "הזמנה לא נמצאה")
                return

            # בניית הודעה עם פרטי ההזמנה
            details = f"📋 הזמנה מספר: {order.order_id}\n"
            details += f"👤 לקוח: {order.customer_id} - {order.customer_name}\n"
            details += f"📅 תאריך: {order.created_at}\n"
            details += f"📊 סטטוס: {order.status}\n\n"
            details += "🛒 פריטים:\n"
            details += "-" * 50 + "\n"

            for item in order.items:
                details += f"  • {item[1]} (ID: {item[0]})\n"
                details += f"    כמות: {item[2]} × {item[3]:.2f} ₪ = {item[4]:.2f} ₪\n"

            details += "-" * 50 + "\n"
            details += f"💰 סה''כ: {order.total_amount:.2f} ₪"

            messagebox.showinfo("פרטי הזמנה", details)
        except Exception as e:
            messagebox.showerror("שגיאה", f"❌ כשל בשליפת פרטי הזמנה: {e}")


# הרצת האפליקציה
if __name__ == "__main__":
    root = tk.Tk()
    app = StoreApp(root)
    root.mainloop()

