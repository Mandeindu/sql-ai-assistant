from database import execute_query
from sql_validator import validate_sql


sql = """
SELECT product_name, SUM(profit) AS total_profit
FROM sales
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 10
"""


# Validate SQL before execution
valid, message = validate_sql(sql)

print("Validation:")
print(message)

if valid:

    result = execute_query(sql)

    print("\nQuery Result:")
    print(result.to_string(index=False))

else:
    print("\nQuery blocked.")