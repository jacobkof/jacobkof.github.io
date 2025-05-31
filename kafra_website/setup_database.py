import sqlite3
import os

# The database file will be created in the same directory as the script.
# This assumes the script is in the 'kafra_website' directory.
DB_PATH = os.path.join(os.path.dirname(__file__), 'kafra.db')

def create_tables():
    """
    Connects to the SQLite database (creates it if it doesn't exist)
    and creates the necessary tables for the KAFRA website.
    """
    conn = None  # Initialize conn to None for the finally block
    try:
        print(f"Attempting to connect to database at: {DB_PATH}")
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Enable foreign key constraint enforcement
        cursor.execute("PRAGMA foreign_keys = ON;")

        # SQL for creating users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'customer', -- e.g., 'customer', 'admin'
                registration_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print("Users table: CREATED successfully or ALREADY EXISTS.")

        # SQL for creating products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                price REAL NOT NULL,
                category TEXT,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                image_url TEXT, -- URL or path to image
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Consider triggers for this later
            );
        """)
        print("Products table: CREATED successfully or ALREADY EXISTS.")

        # SQL for creating orders table
        # Note: user_id references users(id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS orders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount REAL NOT NULL,
                status TEXT NOT NULL DEFAULT 'Pending', -- e.g., 'Pending', 'Processing', 'Shipped', 'Delivered', 'Cancelled'
                shipping_full_name TEXT,
                shipping_address1 TEXT,
                shipping_address2 TEXT,
                shipping_city TEXT,
                shipping_state TEXT,
                shipping_postal_code TEXT,
                shipping_country TEXT,
                shipping_phone TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
                -- ON DELETE CASCADE: if a user is deleted, their orders are also deleted.
                -- Consider if this is the desired behavior or if it should be SET NULL or RESTRICT.
            );
        """)
        print("Orders table: CREATED successfully or ALREADY EXISTS.")

        # SQL for creating order_items table
        # This is a junction table linking orders and products
        # Note: order_id references orders(id), product_id references products(id)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS order_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                order_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL CHECK(quantity > 0), -- Ensure quantity is positive
                price_at_purchase REAL NOT NULL, -- Store the price at the time of purchase
                FOREIGN KEY (order_id) REFERENCES orders (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id) ON DELETE RESTRICT
                -- ON DELETE RESTRICT: prevent deleting a product if it's part of an order item.
                -- Consider if this is desired, or if it should be SET NULL or logged differently.
            );
        """)
        print("Order items table: CREATED successfully or ALREADY EXISTS.")

        conn.commit()
        print("All tables created and changes committed.")

    except sqlite3.Error as e:
        print(f"SQLite error during table creation: {e}")
        if conn:
            conn.rollback() # Rollback changes if an error occurs
            print("Changes rolled back due to error.")
    except Exception as ex:
        print(f"An unexpected error occurred: {ex}")
        if conn:
            conn.rollback()
            print("Changes rolled back due to unexpected error.")
    finally:
        if conn:
            conn.close()
            print("Database connection closed.")

if __name__ == '__main__':
    print("Running database setup script...")
    create_tables()
    print(f"Database setup script 'setup_database.py' finished. If successful, the database '{os.path.basename(DB_PATH)}' should be ready.")
    print(f"Full database path: {DB_PATH}")
