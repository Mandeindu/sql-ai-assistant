import pandas as pd
import sqlite3

# File names
csv_file = "Sample - Superstore.csv"
database_file = "sales.db"

# Load the CSV file
df = pd.read_csv(csv_file, encoding="latin1")

# Clean column names
df.columns = (
    df.columns
    .str.strip()
    .str.lower()
    .str.replace(" ", "_")
)

# Convert date columns
df["order_date"] = pd.to_datetime(
    df["order_date"], errors="coerce"
).dt.strftime("%Y-%m-%d")

df["ship_date"] = pd.to_datetime(
    df["ship_date"], errors="coerce"
).dt.strftime("%Y-%m-%d")

# Convert numeric columns
numeric_columns = [
    "row_id",
    "postal_code",
    "sales",
    "quantity",
    "discount",
    "profit"
]

for column in numeric_columns:
    df[column] = pd.to_numeric(df[column], errors="coerce")

# Connect to SQLite database
connection = sqlite3.connect(database_file)

# Store data in a table called 'sales'
df.to_sql(
    "sales",
    connection,
    if_exists="replace",
    index=False
)

# Create indexes to make queries faster
connection.execute(
    "CREATE INDEX IF NOT EXISTS idx_order_id ON sales(order_id)"
)

connection.execute(
    "CREATE INDEX IF NOT EXISTS idx_customer_id ON sales(customer_id)"
)

connection.execute(
    "CREATE INDEX IF NOT EXISTS idx_product_id ON sales(product_id)"
)

connection.execute(
    "CREATE INDEX IF NOT EXISTS idx_order_date ON sales(order_date)"
)

connection.commit()

# Check number of rows
cursor = connection.cursor()
cursor.execute("SELECT COUNT(*) FROM sales")
row_count = cursor.fetchone()[0]

print("Database created successfully!")
print(f"Table: sales")
print(f"Rows inserted: {row_count}")
print(f"Columns: {len(df.columns)}")

connection.close()