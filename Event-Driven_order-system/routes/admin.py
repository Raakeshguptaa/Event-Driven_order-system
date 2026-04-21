import os
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, Header, Depends
from inventory.model import InventoryUpdate,InventoryCreate
from db.database import get_connection
from tasks.stock_tasks import update_stock_task

load_dotenv()
ADMIN_SECRET = os.getenv("ADMIN_SECRET")

def verify_admin(x_admin_secret: str = Header(...)):
    if x_admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Invalid admin secret")
    return True

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/")
def health_check(): return {"status": "working"}

secure_router = APIRouter(
    prefix="/admin/secure",
    tags=["Admin Secure"],
    dependencies=[Depends(verify_admin)]
)

@secure_router.get("/")
def secure_endpoint(): return {"message": "Access granted"}

@secure_router.get("/view_inventory")
def view_inventory():
    conn = cur = None
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("SELECT product_id, product_name, quantity FROM inventory ORDER BY product_id")
        rows = cur.fetchall()
        inventory = [{"product_id":r[0], "product_name":r[1], "quantity":r[2]} for r in rows]
        return {"inventory": inventory}
    finally:
        if cur: cur.close()
        if conn: conn.close()

@secure_router.post("/add_inventory")
def add_inventory(item: InventoryCreate):
    conn = cur = None
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("INSERT INTO inventory (product_name, quantity) VALUES (%s,%s) RETURNING product_id",
                    (item.prod_name, item.prod_quant))
        pid = cur.fetchone()[0]; conn.commit()
        return {"message":"added","product_id":pid}
    finally:
        if cur: cur.close()
        if conn: conn.close()


@secure_router.put("/update_stock")
def update_stock(item: InventoryUpdate):
    # 🚀 async task instead of direct DB update
    update_stock_task.delay(item.prod_id, item.prod_quant, "increase")
    return {"message": "Stock update scheduled"}

@secure_router.delete("/delete_inventory/{prod_id}")
def delete_inventory(prod_id: int):
    conn = cur = None
    try:
        conn = get_connection(); cur = conn.cursor()
        cur.execute("DELETE FROM inventory WHERE product_id=%s RETURNING product_id", (prod_id,))
        if not cur.fetchone(): raise HTTPException(404,"Not found")
        conn.commit(); return {"message":"deleted"}
    finally:
        if cur: cur.close()
        if conn: conn.close()