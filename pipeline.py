import time

from schema_rag import retrieve_schema
from sql_generator import generate_sql, correct_sql
from sql_validator import validate_sql
from database import execute_query
from visualization import create_chart
from insights import generate_insights


# -----------------------------------
# Clean SQL
# -----------------------------------

def clean_sql(sql):

    sql = sql.strip()

    if sql.startswith("```sql"):
        sql = sql[6:]

    elif sql.startswith("```"):
        sql = sql[3:]

    if sql.endswith("```"):
        sql = sql[:-3]

    return sql.strip()


# -----------------------------------
# Ask Database
# -----------------------------------

def ask_database(
    question,
    vector_store,
    database_path,
    table_name,
    dataframe,
    history=None
):

    if history is None:
        history = []

    start_time = time.perf_counter()

    # -----------------------------------
    # RAG Schema Retrieval
    # -----------------------------------

    schema = retrieve_schema(
        vector_store,
        question,
        dataframe,
        k=4
    )

    rag_time = (
        time.perf_counter()
        - start_time
    )

    # -----------------------------------
    # Reject Unrelated Questions
    # -----------------------------------

    if not schema.strip():

        return {
            "success": False,
            "sql": "",
            "error": (
                "I can only answer questions based "
                "on the uploaded dataset."
            ),
            "corrected": False
        }

    # -----------------------------------
    # Conversation Context
    # -----------------------------------

    conversation_context = (
        build_conversation_context(
            history
        )
    )

    # -----------------------------------
    # Generate SQL
    # -----------------------------------

    sql = generate_sql(
        question,
        schema,
        table_name,
        conversation_context
    )

    sql_time = (
        time.perf_counter()
        - start_time
        - rag_time
    )

    sql = clean_sql(sql)

    # -----------------------------------
    # Validate SQL
    # -----------------------------------

    valid, message = validate_sql(
        sql
    )

    if not valid:

        return {
            "success": False,
            "sql": sql,
            "error": message,
            "corrected": False
        }

    # -----------------------------------
    # Execute SQL
    # -----------------------------------

    try:

        result = execute_query(
            sql,
            database_path
        )

        db_time = (
            time.perf_counter()
            - start_time
            - rag_time
            - sql_time
        )

        # -----------------------------------
        # Empty Result
        # -----------------------------------

        if result.empty:

            return {
                "success": False,
                "sql": sql,
                "error": (
                    "The query executed successfully, "
                    "but no matching data was found."
                ),
                "corrected": False
            }

        # -----------------------------------
        # Visualization
        # -----------------------------------

        chart = create_chart(
            result
        )

        # -----------------------------------
        # Insights
        # -----------------------------------

        insights = generate_insights(
            question,
            result
        )

        # -----------------------------------
        # Timing
        # -----------------------------------

        total_time = (
            time.perf_counter()
            - start_time
        )

        print(
            "\n⏱️ Timing:"
            f"\nRAG: {rag_time:.2f}s"
            f"\nSQL Generation: {sql_time:.2f}s"
            f"\nDatabase: {db_time:.2f}s"
            f"\nTotal: {total_time:.2f}s"
        )

        # -----------------------------------
        # Return Success
        # -----------------------------------

        return {
            "success": True,
            "sql": sql,
            "result": result,
            "chart": chart,
            "insights": insights,
            "corrected": False
        }

    # -----------------------------------
    # SQL Error
    # -----------------------------------

    except Exception as first_error:

        print(
            f"\n⚠️ SQL Error: {first_error}"
        )

        # -----------------------------------
        # Correct SQL
        # -----------------------------------

        corrected_sql = correct_sql(
            question,
            schema,
            table_name,
            sql,
            str(first_error)
        )

        corrected_sql = clean_sql(
            corrected_sql
        )

        # -----------------------------------
        # Validate Corrected SQL
        # -----------------------------------

        valid, message = validate_sql(
            corrected_sql
        )

        if not valid:

            return {
                "success": False,
                "sql": corrected_sql,
                "error": message,
                "corrected": True
            }

        # -----------------------------------
        # Execute Corrected SQL
        # -----------------------------------

        try:

            result = execute_query(
                corrected_sql,
                database_path
            )

            # -----------------------------------
            # Empty Corrected Result
            # -----------------------------------

            if result.empty:

                return {
                    "success": False,
                    "sql": corrected_sql,
                    "error": (
                        "The corrected query executed "
                        "successfully, but no matching "
                        "data was found."
                    ),
                    "corrected": True
                }

            # -----------------------------------
            # Visualization
            # -----------------------------------

            chart = create_chart(
                result
            )

            # -----------------------------------
            # Insights
            # -----------------------------------

            insights = generate_insights(
                question,
                result
            )

            # -----------------------------------
            # Return Corrected Success
            # -----------------------------------

            return {
                "success": True,
                "sql": corrected_sql,
                "result": result,
                "chart": chart,
                "insights": insights,
                "corrected": True
            }

        except Exception as second_error:

            return {
                "success": False,
                "sql": corrected_sql,
                "error": str(second_error),
                "corrected": True
            }


# -----------------------------------
# Build Conversation Context
# -----------------------------------

def build_conversation_context(
    history
):

    if not history:

        return "No previous conversation."

    recent_history = history[-3:]

    context = []

    for item in recent_history:

        result = item.get(
            "result",
            "No result available"
        )

        if hasattr(
            result,
            "to_string"
        ):

            result_text = result.to_string(
                index=False
            )

        else:

            result_text = str(
                result
            )

        # Keep context small
        result_text = result_text[:2000]

        context.append(
            f"""
Previous User Question:
{item['question']}

Previous SQL:
{item['sql']}

Previous Result:
{result_text}
"""
        )

    return "\n".join(
        context
    )