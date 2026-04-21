from db.database import get_connection

def get_inventory_quantity(product_id: int) -> int:
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        cur.execute("SELECT quantity FROM inventory WHERE product_id = %s", (product_id,))
        result = cur.fetchone()
        return result[0] if result else 0
    finally:
        if cur: cur.close()
        if conn: conn.close()