from sql_generator import generate_sql


schema = """
Table: sales

Columns:
row_id
order_id
order_date
ship_date
ship_mode
customer_id
customer_name
segment
country
city
state
postal_code
region
product_id
category
sub_category
product_name
sales
quantity
discount
profit
"""


question = "What are the top 10 products by profit?"

sql = generate_sql(question, schema)

print("\nUser Question:")
print(question)

print("\nGenerated SQL:")
print(sql)