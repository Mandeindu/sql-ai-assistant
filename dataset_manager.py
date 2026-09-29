import io
import re
import sqlite3
import uuid
from pathlib import Path

import pandas as pd


# -----------------------------------
# Configuration
# -----------------------------------

DATA_FOLDER = Path("uploaded_databases")

TABLE_NAME = "uploaded_data"

DATA_FOLDER.mkdir(
    exist_ok=True
)


# -----------------------------------
# Normalize Column Names
# -----------------------------------

def normalize_column_name(column_name):
    """
    Convert column names into
    SQLite/SQL-friendly names.
    """

    column_name = str(
        column_name
    ).strip().lower()

    column_name = re.sub(
        r"[^a-zA-Z0-9]+",
        "_",
        column_name
    )

    column_name = column_name.strip("_")


    if column_name and column_name[0].isdigit():

        column_name = (
            "column_" + column_name
        )


    if not column_name:

        column_name = "column"


    return column_name


# -----------------------------------
# Make Column Names Unique
# -----------------------------------

def make_unique_columns(columns):
    """
    Make sure all column names are unique.
    """

    new_columns = []

    used = {}


    for column in columns:

        column = normalize_column_name(
            column
        )


        if column not in used:

            used[column] = 0

            new_columns.append(
                column
            )

        else:

            used[column] += 1

            new_columns.append(
                f"{column}_{used[column]}"
            )


    return new_columns


# -----------------------------------
# Detect and Normalize Dates
# -----------------------------------

def normalize_date_columns(df):
    """
    Detect date columns and convert them
    into SQLite-friendly YYYY-MM-DD format.
    """

    df = df.copy()


    for column in df.columns:

        series = df[column]


        # Only inspect object/string columns
        if not (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):
            continue


        # Try normal date parsing
        parsed_dates = pd.to_datetime(
            series,
            errors="coerce"
        )


        valid_ratio = (
            parsed_dates.notna().mean()
        )


        # Consider it a date column when
        # at least 80% of non-empty values
        # can be interpreted as dates.
        if valid_ratio >= 0.8:

            df[column] = parsed_dates.dt.strftime(
                "%Y-%m-%d"
            )


    return df


# -----------------------------------
# Load Dataset
# -----------------------------------

def load_dataset(
    file_name,
    file_bytes
):
    """
    Read CSV or Excel file and create
    a SQLite database.

    Returns:
        dataframe
        database_path
        table_name
    """

    extension = Path(
        file_name
    ).suffix.lower()


    # -----------------------------------
    # Read CSV
    # -----------------------------------

    if extension == ".csv":

        try:

            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding="utf-8"
            )

        except UnicodeDecodeError:

            df = pd.read_csv(
                io.BytesIO(file_bytes),
                encoding="latin1"
            )


    # -----------------------------------
    # Read Excel
    # -----------------------------------

    elif extension in [
        ".xlsx",
        ".xls"
    ]:

        df = pd.read_excel(
            io.BytesIO(file_bytes)
        )


    else:

        raise ValueError(
            "Unsupported file format. "
            "Please upload CSV or Excel."
        )


    # -----------------------------------
    # Empty Dataset Check
    # -----------------------------------

    if df.empty:

        raise ValueError(
            "The uploaded dataset is empty."
        )


    # -----------------------------------
    # Normalize Column Names
    # -----------------------------------

    df.columns = make_unique_columns(
        df.columns
    )


    # -----------------------------------
    # Normalize Date Columns
    # -----------------------------------

    df = normalize_date_columns(
        df
    )


    # -----------------------------------
    # Create Unique Database
    # -----------------------------------

    database_name = (
        f"dataset_{uuid.uuid4().hex}.db"
    )

    database_path = (
        DATA_FOLDER / database_name
    )


    # -----------------------------------
    # Create SQLite Database
    # -----------------------------------

    connection = sqlite3.connect(
        database_path
    )


    try:

        df.to_sql(
            TABLE_NAME,
            connection,
            if_exists="replace",
            index=False
        )

    finally:

        connection.close()


    return (
        df,
        str(database_path),
        TABLE_NAME
    )