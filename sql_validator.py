import re


BLOCKED_COMMANDS = [
    "DROP",
    "DELETE",
    "UPDATE",
    "INSERT",
    "ALTER",
    "CREATE",
    "TRUNCATE",
    "REPLACE",
    "ATTACH",
    "DETACH",
]


def validate_sql(sql):
    """
    Validate SQL before execution.

    Only SELECT and WITH queries are allowed.
    """

    if not sql or not sql.strip():
        return False, "SQL query is empty."

    # Remove SQL comments
    cleaned_sql = re.sub(
        r"--.*?$|/\*.*?\*/",
        "",
        sql,
        flags=re.MULTILINE | re.DOTALL
    ).strip()

    if not cleaned_sql:
        return False, "SQL query is empty."

    # Remove one trailing semicolon
    cleaned_sql = cleaned_sql.rstrip(";").strip()

    # Prevent multiple SQL statements
    if ";" in cleaned_sql:
        return False, "Multiple SQL statements are not allowed."

    # Get the first SQL keyword
    match = re.match(
        r"^\s*(SELECT|WITH)\b",
        cleaned_sql,
        re.IGNORECASE
    )

    if not match:
        return False, "Only SELECT and WITH queries are allowed."

    # Check dangerous SQL commands as complete keywords
    for command in BLOCKED_COMMANDS:

        pattern = rf"(?<![A-Za-z0-9_]){command}(?![A-Za-z0-9_])"

        if re.search(
            pattern,
            cleaned_sql,
            re.IGNORECASE
        ):
            return False, f"Blocked SQL command detected: {command}"

    return True, "SQL query is valid."