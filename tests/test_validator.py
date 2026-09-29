from sql_validator import validate_sql


tests = [
    (
        "SELECT product_name FROM uploaded_data",
        True
    ),
    (
        "SELECT update_date FROM uploaded_data",
        True
    ),
    (
        "WITH top_products AS (SELECT * FROM uploaded_data) "
        "SELECT * FROM top_products",
        True
    ),
    (
        "UPDATE uploaded_data SET sales = 0",
        False
    ),
    (
        "DELETE FROM uploaded_data",
        False
    ),
    (
        "DROP TABLE uploaded_data",
        False
    ),
    (
        "SELECT * FROM uploaded_data; DELETE FROM uploaded_data",
        False
    ),
]


for sql, expected in tests:

    valid, message = validate_sql(sql)

    print(
        f"SQL: {sql}\n"
        f"Valid: {valid}\n"
        f"Message: {message}\n"
    )

    assert valid == expected


print("All SQL validator tests passed!")