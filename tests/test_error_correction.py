from schema_rag import vector_store
from sql_generator import correct_sql
from sql_validator import validate_sql
from database import execute_query


question = "What are the top 10 products by profit?"

schema = vector_store.similarity_search(
    question,
    k=1
)[0].page_content


# Intentionally incorrect SQL
wrong_sql = """
SELECT product_name, SUM(profits) AS total_profit
FROM sales
GROUP BY product_name
ORDER BY total_profit DESC
LIMIT 10
"""


print("\nOriginal SQL:")
print(wrong_sql)


# Try executing incorrect SQL
try:

    result = execute_query(wrong_sql)

    print("\nUnexpectedly succeeded:")
    print(result)

except Exception as error:

    print("\nDatabase Error:")
    print(error)

    # Ask Qwen to correct it
    corrected_sql = correct_sql(
        question,
        schema,
        wrong_sql,
        str(error)
    )

    print("\nCorrected SQL:")
    print(corrected_sql)

    # Validate corrected SQL
    valid, message = validate_sql(corrected_sql)

    print("\nValidation:")
    print(message)

    if valid:

        result = execute_query(corrected_sql)

        print("\nCorrected Query Result:")
        print(result.to_string(index=False))