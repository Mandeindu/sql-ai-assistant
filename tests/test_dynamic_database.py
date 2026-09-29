from dataset_manager import load_dataset
from database import execute_query


DATASET_PATH = "Sample - Superstore.csv"


# Read the file
with open(DATASET_PATH, "rb") as file:
    file_bytes = file.read()


# Create SQLite database
df, database_path, table_name = load_dataset(
    DATASET_PATH,
    file_bytes
)


print("\nDataset loaded successfully!")
print("Rows:", len(df))
print("Columns:", len(df.columns))

print("\nColumns:")
print(df.columns.tolist())

print("\nDatabase created at:")
print(database_path)

print("\nTable name:")
print(table_name)


# Test SQL query
sql = f"""
SELECT *
FROM {table_name}
LIMIT 5
"""


result = execute_query(sql, database_path)

print("\nQuery result:")
print(result)