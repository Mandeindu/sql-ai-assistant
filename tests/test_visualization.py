from dataset_manager import load_dataset
from database import execute_query
from visualization import create_chart


DATASET_PATH = "Sample - Superstore.csv"


# Load dataset
with open(DATASET_PATH, "rb") as file:
    file_bytes = file.read()


df, database_path, table_name = load_dataset(
    DATASET_PATH,
    file_bytes
)

print("Dataset loaded successfully!")
print("Database:", database_path)


# Test SQL query
sql = f"""
SELECT category, SUM(sales) AS total_sales
FROM {table_name}
GROUP BY category
ORDER BY total_sales DESC;
"""


print("\nExecuting SQL:")
print(sql)


# Execute query
result = execute_query(
    sql,
    database_path
)


print("\nQuery Result:")
print(result)


# Create chart
chart = create_chart(result)


if chart is not None:
    print("\n✅ Chart created successfully!")
    print("Chart type:", chart.data[0].type)
else:
    print("\n❌ No chart was created.")