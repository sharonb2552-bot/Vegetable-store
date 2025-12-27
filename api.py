from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional

from manage import Manage
from product import Product
from customer import Customer
from DB2 import get_db_connection


# ===============
#     HELPERS
# ===============

def ping():
    """בדיקת חיבור ל-DB"""
    try:
        conn = get_db_connection()
        conn.close()
        return True
    except:
        return False


# ===============
#     MODELS
# ===============

# --- Customers ---
class CustomerIn(BaseModel):
    customer_id: str
    name: str
    address: str | None = None
    phone: str | None = None
    email: str | None = None


class CustomerOut(BaseModel):
    customer_id: str
    name: str
    debt: float
    orders_count: int


# --- Products ---
class ProductOut(BaseModel):
    id: str
    name: str
    price: float
    size: str | None = None
    active: bool


# --- Orders / Items / Payments ---
class OrderItemIn(BaseModel):
    product_id: str
    qty: int
    unit_price: float | None = None


class OrderItemOut(BaseModel):
    product_id: str
    name: str
    qty: int
    unit_price: float
    line_total: float


class OrderItemUpdate(BaseModel):
    qty: int


class OrderIn(BaseModel):
    customer_id: str
    customer_name: str


class OrderOut(BaseModel):
    order_id: str
    customer_id: str
    customer_name: str
    status: str
    total: float
    items: list[OrderItemOut] | None = None


class PaymentIn(BaseModel):
    amount: float


# ==================
# HELPER FUNCTIONS
# ==================

def to_order_out(order) -> OrderOut:
    """ממיר אובייקט Order לפורמט API"""
    items_out: list[OrderItemOut] = []

    for (p_id, name, qty, unit_price, line_total) in order.items:
        items_out.append(OrderItemOut(
            product_id=p_id,
            name=name,
            qty=qty,
            unit_price=unit_price,
            line_total=line_total
        ))

    return OrderOut(
        order_id=order.order_id,
        customer_id=order.customer_id,
        customer_name=order.customer_name,
        status=order.status,
        total=order.total_amount,
        items=items_out
    )


# ===============
# APP SETUP
# ===============

app = FastAPI(title="Store API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# יצירת מופע Store וטעינת מוצרים ראשוניים
store = Manage()

# הוספת מוצרים ראשוניים (אם עדיין לא קיימים ב-DB)
try:
    store.catalog.add_product(Product("P001", "תפוח אדמה לבן", 3.5))
except ValueError:
    pass  # כבר קיים

try:
    store.catalog.add_product(Product("P002", "תפוח אדמה אדום", 4.0))
except ValueError:
    pass

try:
    store.catalog.add_product(Product("P003", "גזר", 2.2))
except ValueError:
    pass


# =============
#    ROUTES
# =============

@app.get("/")
def root():
    return {"message": "Welcome to Store API", "status": "running"}


# --- Products Routes ---

@app.get("/products", response_model=list[ProductOut])
def get_products(q: Optional[str] = None, active: Optional[bool] = None):
    """מחזיר רשימת מוצרים עם אפשרות סינון"""
    # שליפת מוצרים מה-DB
    items = store.catalog.list_all()

    def match(p) -> bool:
        ok = True
        if active is not None:
            ok = ok and (bool(p.active) == active)
        if q:
            ok = ok and (q.lower() in p.name.lower())
        return ok

    return [
        ProductOut(
            id=p.product_id,
            name=p.name,
            price=p.price,
            size=p.size,
            active=p.active,
        )
        for p in items
        if match(p)
    ]


# --- Customer Routes ---

@app.post("/customers", response_model=CustomerOut)
def create_customer(payload: CustomerIn):
    """יוצר לקוח חדש במערכת"""
    if store.get_customer(payload.customer_id) is not None:
        raise HTTPException(status_code=409, detail="Customer already exists")

    c = Customer(
        customer_id=payload.customer_id,
        name=payload.name,
        address=payload.address,
        phone=payload.phone,
        email=payload.email,
    )

    try:
        store.add_customer(c)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return CustomerOut(
        customer_id=c.customer_id,
        name=c.name,
        debt=c.current_balance,
        orders_count=len(c.orders),
    )


@app.get("/customers", response_model=list[CustomerOut])
def list_customers():
    """מחזיר רשימת כל הלקוחות"""
    customers = store.customer_dal.get_all_customers()
    return [
        CustomerOut(
            customer_id=c.customer_id,
            name=c.name,
            debt=c.current_balance,
            orders_count=len(c.orders),
        )
        for c in customers
    ]


@app.get("/customers/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: str):
    """מחזיר פרטי לקוח בודד"""
    customer = store.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return CustomerOut(
        customer_id=customer.customer_id,
        name=customer.name,
        debt=customer.current_balance,
        orders_count=len(customer.orders),
    )


@app.get("/customers/{customer_id}/orders", response_model=list[OrderOut])
def get_customer_orders(customer_id: str):
    """מחזיר את כל ההזמנות של לקוח"""
    customer = store.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    return [to_order_out(order) for order in customer.orders]


# --- Order Routes ---

@app.post("/orders", response_model=OrderOut)
def create_order(payload: OrderIn):
    """יוצר הזמנה חדשה"""
    if store.get_customer(payload.customer_id) is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        order = store.create_order(
            customer_id=payload.customer_id,
            name=payload.customer_name
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


@app.get("/orders", response_model=list[OrderOut])
def list_orders():
    """מחזיר רשימת כל ההזמנות"""
    orders = store.order_dal.get_all_orders()
    return [to_order_out(o) for o in orders]


@app.get("/orders/{order_id}", response_model=OrderOut)
def get_order(order_id: str):
    """מחזיר פרטי הזמנה"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")
    return to_order_out(order)


@app.post("/orders/{order_id}/items", response_model=OrderOut)
def add_item(order_id: str, payload: OrderItemIn):
    """מוסיף פריט להזמנה"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        store.add_item_to_order(
            order_id=order_id,
            product_id=payload.product_id,
            qty=payload.qty,
            unit_price=payload.unit_price
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


@app.put("/orders/{order_id}/items/{product_id}", response_model=OrderOut)
def update_item_qty(order_id: str, product_id: str, payload: OrderItemUpdate):
    """מעדכן כמות של פריט בהזמנה"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        store.update_item_qty(order_id, product_id, payload.qty)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


@app.delete("/orders/{order_id}/items/{product_id}", response_model=OrderOut)
def remove_item(order_id: str, product_id: str):
    """מסיר פריט מהזמנה"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        store.remove_item_from_order(order_id, product_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


@app.post("/orders/{order_id}/complete", response_model=OrderOut)
def complete_order(order_id: str):
    """מסיים הזמנה ושומר ל-DB"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        store.complete_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


@app.post("/orders/{order_id}/cancel", response_model=OrderOut)
def cancel_order(order_id: str):
    """מבטל הזמנה"""
    order = store.get_order(order_id)
    if order is None:
        raise HTTPException(status_code=404, detail="Order not found")

    try:
        store.cancel_order(order_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return to_order_out(order)


# --- Payment Routes ---

@app.post("/customers/{customer_id}/payments")
def add_payment(customer_id: str, payload: PaymentIn):
    """מוסיף תשלום ללקוח"""
    customer = store.get_customer(customer_id)
    if customer is None:
        raise HTTPException(status_code=404, detail="Customer not found")

    try:
        store.add_payment(customer_id, payload.amount)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # רענון הלקוח אחרי התשלום
    customer = store.get_customer(customer_id)
    return {
        "customer_id": customer.customer_id,
        "new_debt": customer.current_balance,
        "payment_amount": payload.amount
    }


# --- Debug Routes ---

@app.get("/__debug")
def debug_state():
    """מידע דיבאג על מצב המערכת"""
    try:
        products = store.catalog.list_all()
        customers = store.customer_dal.get_all_customers()
        orders = store.order_dal.get_all_orders()

        return {
            "products_count": len(products),
            "customers_count": len(customers),
            "orders_count": len(orders),
            "db_connection": "ok"
        }
    except Exception as e:
        return {
            "error": str(e),
            "db_connection": "failed"
        }


@app.get("/__db_ping")
def db_ping():
    """בדיקת חיבור ל-DB"""
    try:
        return {"mysql": "ok" if ping() else "fail"}
    except Exception as e:
        return {"mysql": "error", "detail": str(e)}