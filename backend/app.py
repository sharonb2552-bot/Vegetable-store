"""
API לחנות האינטרנטית - עם מערכת התחברות
"""

from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import mysql.connector
import uuid
from datetime import datetime
import os

app = Flask(__name__, static_folder='../frontend', static_url_path='')
CORS(app)

# ===================
# הגדרות DB
# ===================
DB_CONFIG = {
    'user': 'root',
    'password': 'TmMGuhdXgQuVvyraaaYkJyRwEKsgOQcO',
    'host': 'metro.proxy.rlwy.net',
    'port': 53247,
    'database': 'railway'
}


def get_db():
    return mysql.connector.connect(**DB_CONFIG)


# ===================
# הגשת האתר
# ===================

@app.route('/')
def serve_index():
    return app.send_static_file('index.html')


@app.route('/images/<path:filename>')
def serve_images(filename):
    return send_from_directory('../frontend/images', filename)


# ===================
# הזדהות
# ===================

@app.route('/api/auth/register', methods=['POST'])
def register():
    """הרשמת לקוח חדש"""
    try:
        data = request.json

        if not data.get('name') or not data.get('phone') or not data.get('id_number'):
            return jsonify({'error': 'שם, טלפון ותעודת זהות הם שדות חובה'}), 400

        phone = data['phone'].strip()
        id_number = data['id_number'].strip()
        customer_type = data.get('customer_type', 'retail')

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        # בדיקה אם תעודת הזהות כבר קיימת
        cursor.execute("SELECT * FROM Customers WHERE customer_id = %s", (id_number,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'תעודת זהות זו כבר רשומה במערכת'}), 409

        # בדיקה אם השם כבר קיים
        cursor.execute("SELECT * FROM Customers WHERE name = %s", (data['name'],))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'שם זה כבר קיים במערכת, אנא בחר שם אחר'}), 409

        # בדיקה אם הטלפון כבר קיים
        cursor.execute("SELECT * FROM Customers WHERE phone = %s", (phone,))
        if cursor.fetchone():
            conn.close()
            return jsonify({'error': 'מספר טלפון זה כבר רשום במערכת'}), 409

        customer_id = id_number

        cursor.execute("""
            INSERT INTO Customers (customer_id, name, phone, address, email, balance, customer_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id,
            data['name'],
            phone,
            data.get('address'),
            data.get('email'),
            0.0,
            customer_type
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'customer_id': customer_id,
            'name': data['name'],
            'phone': phone,
            'customer_type': customer_type
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/auth/login', methods=['POST'])
def login():
    """התחברות לקוח קיים"""
    try:
        data = request.json
        name = data.get('name', '').strip()

        if not name:
            return jsonify({'error': 'שם הוא שדה חובה'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, name, phone, address, email, balance, customer_type 
            FROM Customers WHERE name = %s
        """, (name,))

        customer = cursor.fetchone()
        conn.close()

        if not customer:
            return jsonify({'error': 'שם לא נמצא במערכת'}), 404

        return jsonify({
            'success': True,
            'customer_id': customer['customer_id'],
            'name': customer['name'],
            'phone': customer['phone'],
            'address': customer['address'],
            'email': customer['email'],
            'balance': float(customer['balance']),
            'customer_type': customer['customer_type'] or 'retail'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================
# מוצרים
# ===================

@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT product_id, name, price, size, unit, active 
            FROM Products 
            WHERE active = TRUE
            ORDER BY name, size
        """)

        products = []
        for row in cursor.fetchall():
            products.append({
                'id': row['product_id'],
                'name': row['name'],
                'price': float(row['price']),
                'size': row['size'],
                'unit': row['unit'] or 'ק"ג',
                'active': bool(row['active'])
            })

        conn.close()
        return jsonify(products)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================
# לקוחות
# ===================

@app.route('/api/customers', methods=['GET'])
def get_customers():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, name, phone, address, email, balance, customer_type 
            FROM Customers ORDER BY name
        """)

        customers = []
        for row in cursor.fetchall():
            customers.append({
                'id': row['customer_id'],
                'name': row['name'],
                'phone': row['phone'],
                'address': row['address'],
                'email': row['email'],
                'balance': float(row['balance']),
                'customer_type': row['customer_type'] or 'retail'
            })

        conn.close()
        return jsonify(customers)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.json

        if not data.get('name'):
            return jsonify({'error': 'שם לקוח הוא שדה חובה'}), 400

        customer_id = data.get('customer_id') or f"C{datetime.now().strftime('%Y%m%d%H%M%S')}"
        customer_type = data.get('customer_type', 'retail')

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO Customers (customer_id, name, phone, address, email, balance, customer_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """, (
            customer_id,
            data['name'],
            data.get('phone'),
            data.get('address'),
            data.get('email'),
            0.0,
            customer_type
        ))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'customer_id': customer_id
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers/<customer_id>', methods=['GET'])
def get_customer(customer_id):
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, name, phone, address, email, balance, customer_type 
            FROM Customers WHERE customer_id = %s
        """, (customer_id,))

        row = cursor.fetchone()
        conn.close()

        if not row:
            return jsonify({'error': 'לקוח לא נמצא'}), 404

        return jsonify({
            'id': row['customer_id'],
            'name': row['name'],
            'phone': row['phone'],
            'address': row['address'],
            'email': row['email'],
            'balance': float(row['balance']),
            'customer_type': row['customer_type'] or 'retail'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================
# הזמנות
# ===================

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.order_id, o.customer_id, c.name as customer_name, 
                   o.status, o.total, o.created_at
            FROM Orders o
            LEFT JOIN Customers c ON o.customer_id = c.customer_id
            ORDER BY o.created_at DESC
        """)

        orders = []
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT oi.product_id, p.name, p.size, oi.qty, oi.unit_price, oi.line_total
                FROM Order_items oi
                LEFT JOIN Products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (row['order_id'],))

            items = []
            for item in cursor.fetchall():
                name = item['name']
                if item['size']:
                    name += f" ({item['size']})"
                items.append({
                    'product_id': item['product_id'],
                    'name': name,
                    'qty': float(item['qty']),
                    'unit_price': float(item['unit_price']),
                    'line_total': float(item['line_total'])
                })

            orders.append({
                'order_id': row['order_id'],
                'customer_id': row['customer_id'],
                'customer_name': row['customer_name'],
                'status': row['status'],
                'total': float(row['total']),
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'items': items
            })

        conn.close()
        return jsonify(orders)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.json

        if not data.get('customer_id'):
            return jsonify({'error': 'חסר מזהה לקוח'}), 400
        if not data.get('items') or len(data['items']) == 0:
            return jsonify({'error': 'ההזמנה חייבת להכיל לפחות פריט אחד'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("SELECT customer_id, customer_type FROM Customers WHERE customer_id = %s",
                       (data['customer_id'],))
        customer = cursor.fetchone()
        if not customer:
            conn.close()
            return jsonify({'error': 'לקוח לא נמצא'}), 404

        # חישוב הנחה לפי סוג לקוח
        discount = 0.8 if customer['customer_type'] == 'wholesale' else 1.0

        order_id = f"ORD_{datetime.now().strftime('%Y%m%d')}_{str(uuid.uuid4())[:8].upper()}"

        total = 0.0
        items_to_insert = []

        for item in data['items']:
            cursor.execute("""
                SELECT product_id, name, price, active 
                FROM Products WHERE product_id = %s
            """, (item['product_id'],))

            product = cursor.fetchone()
            if not product:
                conn.close()
                return jsonify({'error': f"מוצר {item['product_id']} לא נמצא"}), 404

            if not product['active']:
                conn.close()
                return jsonify({'error': f"מוצר {product['name']} לא פעיל"}), 400

            qty = float(item['qty'])
            unit_price = float(product['price']) * discount
            line_total = qty * unit_price
            total += line_total

            items_to_insert.append({
                'product_id': item['product_id'],
                'qty': qty,
                'unit_price': unit_price,
                'line_total': line_total
            })

        cursor.execute("""
            INSERT INTO Orders (order_id, customer_id, status, total)
            VALUES (%s, %s, %s, %s)
        """, (order_id, data['customer_id'], 'COMPLETED', total))

        for item in items_to_insert:
            cursor.execute("""
                INSERT INTO Order_items (order_id, product_id, qty, unit_price, line_total)
                VALUES (%s, %s, %s, %s, %s)
            """, (order_id, item['product_id'], item['qty'],
                  item['unit_price'], item['line_total']))

        cursor.execute("""
            UPDATE Customers SET balance = balance + %s WHERE customer_id = %s
        """, (total, data['customer_id']))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'order_id': order_id,
            'total': total
        }), 201

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/customers/<customer_id>/orders', methods=['GET'])
def get_customer_orders(customer_id):
    """מחזיר את ההזמנות של לקוח ספציפי"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT order_id, status, total, created_at
            FROM Orders 
            WHERE customer_id = %s
            ORDER BY created_at DESC
        """, (customer_id,))

        orders = []
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT oi.product_id, p.name, p.size, oi.qty, oi.unit_price, oi.line_total
                FROM Order_items oi
                LEFT JOIN Products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (row['order_id'],))

            items = []
            for item in cursor.fetchall():
                name = item['name']
                if item['size']:
                    name += f" ({item['size']})"
                items.append({
                    'product_id': item['product_id'],
                    'name': name,
                    'qty': float(item['qty']),
                    'unit_price': float(item['unit_price']),
                    'line_total': float(item['line_total'])
                })

            orders.append({
                'order_id': row['order_id'],
                'status': row['status'],
                'total': float(row['total']),
                'created_at': row['created_at'].isoformat() if row['created_at'] else None,
                'items': items
            })

        conn.close()
        return jsonify(orders)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================
# תשלומים
# ===================

@app.route('/api/customers/<customer_id>/payments', methods=['POST'])
def add_payment(customer_id):
    try:
        data = request.json
        amount = float(data.get('amount', 0))

        if amount <= 0:
            return jsonify({'error': 'סכום התשלום חייב להיות חיובי'}), 400

        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT customer_id, balance FROM Customers WHERE customer_id = %s
        """, (customer_id,))

        customer = cursor.fetchone()
        if not customer:
            conn.close()
            return jsonify({'error': 'לקוח לא נמצא'}), 404

        current_balance = float(customer['balance'])
        if amount > current_balance:
            conn.close()
            return jsonify({'error': 'סכום התשלום גדול מהחוב'}), 400

        new_balance = current_balance - amount
        cursor.execute("""
            UPDATE Customers SET balance = %s WHERE customer_id = %s
        """, (new_balance, customer_id))

        conn.commit()
        conn.close()

        return jsonify({
            'success': True,
            'new_balance': new_balance
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===================
# בדיקות
# ===================

@app.route('/api/health', methods=['GET'])
def health_check():
    try:
        conn = get_db()
        conn.close()
        return jsonify({'status': 'ok', 'database': 'connected'})
    except Exception as e:
        return jsonify({'status': 'error', 'database': str(e)}), 500


# ===================
# ניהול (Admin)
# ===================

@app.route('/admin')
def serve_admin():
    return app.send_static_file('admin.html')


@app.route('/api/admin/orders', methods=['GET'])
def get_all_orders_admin():
    """מחזיר את כל ההזמנות עם פרטים מלאים למנהל"""
    try:
        conn = get_db()
        cursor = conn.cursor(dictionary=True)

        cursor.execute("""
            SELECT o.order_id, o.customer_id, c.name as customer_name, c.phone,
                   c.address, c.customer_type, o.status, o.total, o.created_at
            FROM Orders o
            LEFT JOIN Customers c ON o.customer_id = c.customer_id
            ORDER BY o.created_at DESC
        """)

        orders = []
        for row in cursor.fetchall():
            cursor.execute("""
                SELECT oi.product_id, p.name, p.size, oi.qty, oi.unit_price, oi.line_total
                FROM Order_items oi
                LEFT JOIN Products p ON oi.product_id = p.product_id
                WHERE oi.order_id = %s
            """, (row['order_id'],))

            items = []
            for item in cursor.fetchall():
                name = item['name']
                if item['size']:
                    name += f" ({item['size']})"
                items.append({
                    'product_id': item['product_id'],
                    'name': name,
                    'qty': float(item['qty']),
                    'unit_price': float(item['unit_price']),
                    'line_total': float(item['line_total'])
                })

            orders.append({
                'order_id': row['order_id'],
                'customer_id': row['customer_id'],
                'customer_name': row['customer_name'],
                'phone': row['phone'],
                'address': row['address'],
                'customer_type': row['customer_type'],
                'status': row['status'],
                'total': float(row['total']),
                'created_at': row['created_at'].strftime('%d/%m/%Y %H:%M') if row['created_at'] else None,
                'items': items
            })

        conn.close()
        return jsonify(orders)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/admin/orders/<order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """עדכון סטטוס הזמנה"""
    try:
        data = request.json
        new_status = data.get('status')

        if not new_status:
            return jsonify({'error': 'חסר סטטוס'}), 400

        conn = get_db()
        cursor = conn.cursor()

        cursor.execute("""
            UPDATE Orders SET status = %s WHERE order_id = %s
        """, (new_status, order_id))

        conn.commit()
        conn.close()

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("🚀 מפעיל את השרת...")
    print("📍 http://localhost:8080")
    app.run(debug=True, port=8080, host='0.0.0.0')