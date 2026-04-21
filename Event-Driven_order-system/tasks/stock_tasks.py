import sys
from pathlib import Path

# Add parent directory to path so we can import celery_app
sys.path.insert(0, str(Path(__file__).parent.parent))

from celery_app import celery_app
from db.database import get_connection

@celery_app.task(name="tasks.stock_tasks.update_stock_task", bind=True)
def update_stock_task(self, product_id: int, quantity: int, operation: str):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        # 🔒 Lock row for concurrency safety
        cur.execute(
            "SELECT quantity FROM inventory WHERE product_id=%s FOR UPDATE",
            (product_id,)
        )
        row = cur.fetchone()

        if not row:
            return "Product not found"

        current_stock = row[0]

        if operation == "decrease":
            if current_stock < quantity:
                return "Not enough stock"

            cur.execute(
                "UPDATE inventory SET quantity = quantity - %s WHERE product_id=%s",
                (quantity, product_id)
            )

        elif operation == "increase":
            cur.execute(
                "UPDATE inventory SET quantity = quantity + %s WHERE product_id=%s",
                (quantity, product_id)
            )

        conn.commit()
        return "Stock updated"

    except Exception as e:
        if conn:
            conn.rollback()
        raise self.retry(exc=e, countdown=5)

    finally:
        if cur: cur.close()
        if conn: conn.close()