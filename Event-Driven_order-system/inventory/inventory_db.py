from db.database import get_connection

conn = None
cur = None

try:
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS inventory (
            product_id SERIAL PRIMARY KEY,
            product_name VARCHAR(100),
            product_quantity INT
        );
    """)
    
    conn.commit()
    print("Inventory table created successfully!")

except Exception as error:
    print(f"Error: {error}")

finally:
    if cur:
        cur.close()
    if conn:
        conn.close()