import streamlit as st
import requests
import pandas as pd

BASE_URL = "http://127.0.0.1:8000"
st.set_page_config(page_title="Order System", page_icon="📦", layout="wide")
st.title("📦 Order Management System")

menu = st.sidebar.radio("Menu", ["Client", "Admin"])

# --- helpers ---
def check_api():
    try:
        r = requests.get(f"{BASE_URL}/health", timeout=2)
        return r.ok
    except:
        return False

# FIX: use normal if-else (not one-line)
if check_api():
    st.sidebar.success("API Online ✅")
else:
    st.sidebar.error("API Offline ❌")

# Client helpers
def create_order(pid, name, qty):
    return requests.post(f"{BASE_URL}/create_order", 
                         json={"prod_id":int(pid), "prod_name":name, "prod_quant":int(qty)})

def get_orders():
    return requests.get(f"{BASE_URL}/order")

# Admin helpers
def api_headers(secret): 
    return {"x-admin-secret": secret}

def get_inv(secret):
    return requests.get(f"{BASE_URL}/admin/secure/view_inventory", headers=api_headers(secret))

def add_inv(secret, name, qty):
    return requests.post(f"{BASE_URL}/admin/secure/add_inventory", 
                         headers=api_headers(secret),
                         json={"prod_name": name, "prod_quant": int(qty)})

def upd_inv(secret, pid, qty):
    return requests.put(f"{BASE_URL}/admin/secure/update_stock", 
                        headers=api_headers(secret),
                        json={"prod_id": int(pid), "prod_quant": int(qty)})

def del_inv(secret, pid):
    return requests.delete(f"{BASE_URL}/admin/secure/delete_inventory/{pid}", 
                           headers=api_headers(secret))

# ================= CLIENT =================
if menu == "Client":
    st.header("🛒 Client Dashboard")
    tab1, tab2 = st.tabs(["Create Order", "My Orders"])

    with tab1:
        st.subheader("Place New Order")
        with st.form("order_form", clear_on_submit=False):
            c1, c2 = st.columns(2)
            prod_id = c1.number_input("Product ID", min_value=1, step=1, value=1)
            prod_quant = c2.number_input("Quantity", min_value=1, step=1, value=1)
            prod_name = st.text_input("Product Name", placeholder="e.g. iphone7")
            
            submit = st.form_submit_button("Create Order", type="primary", use_container_width=True)
            if submit:
                r = create_order(prod_id, prod_name, prod_quant)
                if r.status_code in [200, 201]:
                    st.success(f"✅ Order created! {r.json()}")
                    st.balloons()
                else:
                    try:
                        st.error(r.json().get('detail', 'Failed'))
                    except:
                        st.error("Failed to create order")

    with tab2:
        st.subheader("Order History")
        if st.button("🔄 Refresh Orders"):
            r = get_orders()
            if r.ok:
                orders = r.json().get("orders", [])
                if orders:
                    st.dataframe(pd.DataFrame(orders), use_container_width=True, hide_index=True)
                else:
                    st.info("No orders yet")
            else:
                st.error("Cannot load orders")

# ================= ADMIN =================
else:
    st.header("🔐 Admin Inventory Control")
    secret = st.text_input("Admin Secret", type="password")

    if not secret:
        st.info("Enter admin secret")
        st.stop()

    # load inventory
    if "inv" not in st.session_state:
        r = get_inv(secret)
        st.session_state.inv = r.json().get("inventory", []) if r.ok else []

    if st.button("🔄 Refresh Inventory"):
        r = get_inv(secret)
        if r.ok:
            st.session_state.inv = r.json().get("inventory", [])
            st.toast("Refreshed")
        else:
            st.error(r.json())

    df = pd.DataFrame(st.session_state.inv)

    st.subheader("Current Stock")
    if not df.empty:
        st.dataframe(df, use_container_width=True, hide_index=True,
            column_config={"product_id":"ID", "product_name":"Product", "quantity":"Qty"})
    else:
        st.warning("No inventory found")

    st.divider()
    c1, c2, c3 = st.columns(3)

    with c1:
        st.markdown("#### ➕ Add Product")
        with st.form("add"):
            name = st.text_input("Name")
            qty = st.number_input("Quantity", 0, 10000, 1)
            if st.form_submit_button("Add", use_container_width=True):
                r = add_inv(secret, name, qty)
                st.success("Added") if r.ok else st.error(r.json())
                if r.ok: st.rerun()

    with c2:
        st.markdown("#### ✏️ Update Stock")
        with st.form("upd"):
            if not df.empty:
                pid = st.selectbox("Product", df['product_id'],
                    format_func=lambda x: f"{x} - {df.loc[df.product_id==x, 'product_name'].values[0]}")
                cur_qty = int(df.loc[df.product_id==pid, 'quantity'].values[0])
                new_qty = st.number_input("New Qty", 0, 10000, cur_qty)
                if st.form_submit_button("Update", use_container_width=True):
                    r = upd_inv(secret, pid, new_qty)
                    st.success("Updated") if r.ok else st.error(r.json())
                    if r.ok: st.rerun()
            else:
                st.caption("Add a product first")

    with c3:
        st.markdown("#### 🗑️ Remove")
        with st.form("del"):
            if not df.empty:
                pid2 = st.selectbox("Product", df['product_id'], key="del2",
                    format_func=lambda x: f"{x} - {df.loc[df.product_id==x, 'product_name'].values[0]}")
                if st.form_submit_button("Delete", type="primary", use_container_width=True):
                    r = del_inv(secret, pid2)
                    st.success("Deleted") if r.ok else st.error(r.json())
                    if r.ok: st.rerun()
            else:
                st.caption("Add a product first")