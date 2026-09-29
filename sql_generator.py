import streamlit as st
from langchain_ollama import ChatOllama


# -----------------------------------
# LLM
# -----------------------------------

@st.cache_resource
def get_llm():

    return ChatOllama(
        model="qwen2.5-coder:3b",
        temperature=0,
        num_predict=256
    )


# -----------------------------------
# Detect Follow-up Question
# -----------------------------------

def is_follow_up_question(question):
    """
    Detect whether the current question depends
    on the previous conversation.
    """

    question_lower = question.lower().strip()

    follow_up_phrases = [
        "their",
        "them",
        "those",
        "these",
        "same",
        "previous",
        "above",
        "that",
        "what about",
        "how about",
        "and their",
        "and those",
        "also show",
        "also calculate",
        "same products",
        "same customers",
        "same orders"
    ]

    for phrase in follow_up_phrases:

        if phrase in question_lower:
            return True

    return False


# -----------------------------------
# Generate SQL
# -----------------------------------

def generate_sql(
    question,
    schema,
    table_name,
    conversation_context="No previous conversation."
):
    """
    Convert a natural language question into SQLite SQL.
    """

    # -----------------------------------
    # Decide Whether History Is Needed
    # -----------------------------------

    if is_follow_up_question(question):

        previous_context = conversation_context

    else:

        previous_context = (
            "This is a new independent question. "
            "Ignore previous questions and results."
        )


    # -----------------------------------
    # SQL Prompt
    # -----------------------------------

    prompt = f"""
You are a SQLite SQL assistant for data analysis.

CURRENT USER QUESTION:
{question}

TABLE:
{table_name}

SCHEMA:
{schema}

CONVERSATION CONTEXT:
{previous_context}

IMPORTANT:

The CURRENT USER QUESTION always has the highest priority.

If this is a new independent question, completely ignore
previous questions and previous SQL.

Only use previous conversation when the current question
clearly refers to previous results.

RULES:

1. Return ONLY SQL.
2. Do not return markdown.
3. Do not return explanations.
4. Use only table "{table_name}".
5. Use only columns present in the schema.
6. Use valid SQLite syntax.
7. Only SELECT or WITH queries are allowed.
8. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
   TRUNCATE, REPLACE, ATTACH or DETACH.
9. Never invent columns.
10. Answer the CURRENT USER QUESTION directly.

-----------------------------------
AGGREGATION
-----------------------------------

If the user asks for total sales:

SELECT SUM(sales) AS total_sales
FROM {table_name};

If the user asks for total profit:

SELECT SUM(profit) AS total_profit
FROM {table_name};

If the user asks for average sales:

SELECT AVG(sales) AS average_sales
FROM {table_name};

If the user asks for average profit:

SELECT AVG(profit) AS average_profit
FROM {table_name};

If the user asks for total quantity:

SELECT SUM(quantity) AS total_quantity
FROM {table_name};

If the user asks how many records:

SELECT COUNT(*) AS record_count
FROM {table_name};

If the user asks how many orders and order_id exists:

SELECT COUNT(DISTINCT order_id) AS order_count
FROM {table_name};

If the user asks how many customers and customer_id exists:

SELECT COUNT(DISTINCT customer_id) AS customer_count
FROM {table_name};

If the user asks how many products and product_id exists:

SELECT COUNT(DISTINCT product_id) AS product_count
FROM {table_name};

-----------------------------------
GROUPING
-----------------------------------

When the question asks for a metric "by" another column,
GROUP BY that column.

Example:

Question:
Sales by region

SQL:

SELECT
    region,
    SUM(sales) AS total_sales
FROM {table_name}
GROUP BY region
ORDER BY total_sales DESC;

Example:

Question:
Profit by category

SQL:

SELECT
    category,
    SUM(profit) AS total_profit
FROM {table_name}
GROUP BY category
ORDER BY total_profit DESC;

-----------------------------------
DATE COLUMN SELECTION
-----------------------------------

When the dataset contains both order_date and ship_date:

For questions about:

sales over time
sales trend
sales by month
sales by year
orders over time
orders trend
profit over time
profit trend
quantity over time
business performance over time

PREFER:

order_date

because the analysis should normally be based on
when the order was placed.

Use ship_date ONLY when the question specifically
mentions shipping, shipment, delivery, or ship date.

Examples:

"Show sales over time"
→ use order_date

"Show monthly sales"
→ use order_date

"Show sales trend by year"
→ use order_date

"Show shipments over time"
→ use ship_date

"Show shipping trend"
→ use ship_date

"Sales by ship date"
→ use ship_date

-----------------------------------
DATE GROUPING
-----------------------------------

For "over time", "trend", or a general time-series
question:

Prefer MONTHLY aggregation.

Use:

strftime('%Y-%m', order_date)

Example:

SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(sales) AS total_sales
FROM {table_name}
GROUP BY month
ORDER BY month;

For "by year":

SELECT
    strftime('%Y', order_date) AS year,
    SUM(sales) AS total_sales
FROM {table_name}
GROUP BY year
ORDER BY year;

For "by month":

SELECT
    strftime('%Y-%m', order_date) AS month,
    SUM(sales) AS total_sales
FROM {table_name}
GROUP BY month
ORDER BY month;

For "daily sales" or "sales by date":

Group by the actual date.

Do NOT return every transaction date for a general
"over time" question.

-----------------------------------
RANKING
-----------------------------------

For "top N":

1. GROUP BY the requested entity.
2. Calculate the requested metric.
3. ORDER BY the metric DESC.
4. LIMIT N.

Example:

Question:
Top 5 products by sales

SQL:

SELECT
    product_name,
    SUM(sales) AS total_sales
FROM {table_name}
GROUP BY product_name
ORDER BY total_sales DESC
LIMIT 5;

For "lowest", "bottom N", or "worst":

ORDER BY the metric ASC.

-----------------------------------
FOLLOW-UP QUESTIONS
-----------------------------------

Only use previous conversation when the current question
clearly refers to previous results.

Previous:

Top 5 products by sales

Current:

What about their profit?

The same 5 products must be preserved.

Use:

SELECT
    product_name,
    SUM(profit) AS total_profit
FROM {table_name}
WHERE product_name IN (
    SELECT product_name
    FROM {table_name}
    GROUP BY product_name
    ORDER BY SUM(sales) DESC
    LIMIT 5
)
GROUP BY product_name
ORDER BY total_profit DESC;

Do NOT create a new top 5 based on profit.

Previous:

Top 5 products by sales

Current:

What about their quantity?

Calculate quantity for the SAME 5 products.

-----------------------------------
FINAL INSTRUCTION
-----------------------------------

Focus primarily on the CURRENT USER QUESTION.

CURRENT USER QUESTION:
{question}

SQL:
"""

    response = get_llm().invoke(prompt)

    return response.content.strip()


# -----------------------------------
# Correct SQL
# -----------------------------------

def correct_sql(
    question,
    schema,
    table_name,
    sql,
    error
):
    """
    Correct an SQL query after a database error.
    """

    prompt = f"""
Fix this SQLite SQL query.

CURRENT USER QUESTION:
{question}

TABLE:
{table_name}

SCHEMA:
{schema}

GENERATED SQL:
{sql}

DATABASE ERROR:
{error}

RULES:

1. Return ONLY corrected SQL.
2. Do not return markdown.
3. Do not return explanations.
4. Use only table "{table_name}".
5. Use only columns present in the schema.
6. Use valid SQLite syntax.
7. Only SELECT or WITH queries are allowed.
8. Never use INSERT, UPDATE, DELETE, DROP, ALTER, CREATE,
   TRUNCATE, REPLACE, ATTACH or DETACH.
9. Never invent columns.
10. Preserve the meaning of the CURRENT USER QUESTION.
11. Use GROUP BY when aggregation by a category is required.
12. Use SUM, AVG, COUNT, MIN or MAX when appropriate.
13. For general time-series questions, prefer order_date
    when both order_date and ship_date exist.
14. Use ship_date only when the question specifically
    concerns shipping or shipment dates.
15. For "over time" questions, prefer monthly aggregation.

CORRECTED SQL:
"""

    response = get_llm().invoke(prompt)

    return response.content.strip()