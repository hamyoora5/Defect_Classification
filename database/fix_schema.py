import psycopg2
import os

def alter_schema():
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="15432",
            database="defect_db",
            user="postgres",
            password="1234"
        )
        cursor = conn.cursor()
        print("Altering table column lengths...")
        cursor.execute("ALTER TABLE inspection_results ALTER COLUMN product_id TYPE VARCHAR(255);")
        cursor.execute("ALTER TABLE inspection_results ALTER COLUMN quality TYPE VARCHAR(50);")
        cursor.execute("ALTER TABLE inspection_results ALTER COLUMN defect_type TYPE VARCHAR(255);")
        conn.commit()
        cursor.close()
        conn.close()
        print("Schema altered successfully.")
    except Exception as e:
        print(f"Error altering schema: {e}")

if __name__ == "__main__":
    alter_schema()
