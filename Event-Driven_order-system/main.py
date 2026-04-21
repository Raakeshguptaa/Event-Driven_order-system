from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from order.model import Create_order
from db.database import get_connection
from inventory.inv_service import get_inventory_quantity
from routes.admin import router, secure_router


from tasks.stock_tasks import update_stock_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS inventory (
                product_id SERIAL PRIMARY KEY,
                product_name VARCHAR(100) NOT NULL,
                quantity INTEGER NOT NULL DEFAULT 0
            );
        """)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                order_id SERIAL PRIMARY KEY,
                product_id INTEGER NOT NULL,
                product_name VARCHAR(100) NOT NULL,
                product_quantity INTEGER NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

        conn.commit()
        print("Database tables initialized successfully!")

    finally:
        if cur: cur.close()
        if conn: conn.close()

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(router)
app.include_router(secure_router)


@app.get("/")
def status():
    return {"message": "API Running"}


@app.get("/health")
def health():
    return {"message": "API Healthy"}


# 🛒 CREATE ORDER (ASYNC STOCK UPDATE)
@app.post("/create_order")
def create_order(create: Create_order):
    inv_quantity = get_inventory_quantity(create.prod_id)

    if create.prod_quant > inv_quantity:
        raise HTTPException(status_code=400, detail="Out of stock")

    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

      
        cur.execute("""
            INSERT INTO orders (product_id, product_name, product_quantity)
            VALUES (%s, %s, %s) RETURNING order_id;
        """, (create.prod_id, create.prod_name, create.prod_quant))

        order_id = cur.fetchone()[0]
        conn.commit()


        update_stock_task.delay(create.prod_id, create.prod_quant, "decrease")

        return {
            "message": "Order created successfully",
            "order_id": order_id,
            "note": "Stock update in background"
        }

    except Exception as e:
        if conn:
            conn.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur: cur.close()
        if conn: conn.close()


@app.get("/order")
def get_orders():
    conn = None
    cur = None
    try:
        conn = get_connection()
        cur = conn.cursor()

        cur.execute("SELECT * FROM orders")
        rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description] if cur.description else []

        return {"orders": [dict(zip(columns, row)) for row in rows]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    finally:
        if cur: cur.close()
        if conn: conn.close()