import sqlite3
import re

import pandas as pd


def execute_query(sql, database_path):
    """
    Execute a read-only SQL query on the selected SQLite database.
    """

    if not sql or not sql.strip():
        raise ValueError("SQL query is empty.")

    # Remove SQL comments
    cleaned_sql = re.sub(
        r"--.*?$|/\*.*?\*/",
        "",
        sql,
        flags=re.MULTILINE | re.DOTALL
    ).strip()

    # Remove one trailing semicolon
    cleaned_sql = cleaned_sql.rstrip(";").strip()

    # Only SELECT and WITH queries are allowed
    if not re.match(
        r"^(SELECT|WITH)\b",
        cleaned_sql,
        re.IGNORECASE
    ):
        raise ValueError(
            "Only read-only SELECT or WITH queries are allowed."
        )

    # Prevent multiple SQL statements
    if ";" in cleaned_sql:
        raise ValueError(
            "Multiple SQL statements are not allowed."
        )

    # Open SQLite database in read-only mode
    connection = sqlite3.connect(
        f"file:{database_path}?mode=ro",
        uri=True
    )

    try:

        df = pd.read_sql_query(
            cleaned_sql,
            connection
        )

        return df

    finally:

        connection.close()