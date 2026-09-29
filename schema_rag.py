import streamlit as st
import pandas as pd

from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# -----------------------------------
# Embeddings
# -----------------------------------

@st.cache_resource
def get_embeddings():

    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )


# -----------------------------------
# Create Schema Documents
# -----------------------------------

def create_schema_documents(df, table_name):

    documents = []

    # -----------------------------------
    # Table Description
    # -----------------------------------

    table_description = f"""
Table name: {table_name}

This table contains data uploaded by the user.

Number of rows: {len(df)}
Number of columns: {len(df.columns)}

Columns:
{", ".join(df.columns)}
"""

    documents.append(
        Document(
            page_content=table_description,
            metadata={
                "type": "table",
                "table": table_name
            }
        )
    )

    # -----------------------------------
    # Column Documents
    # -----------------------------------

    for column in df.columns:

        series = df[column]

        dtype = str(series.dtype)

        # -----------------------------------
        # Detect Date Columns
        # -----------------------------------

        date_series = pd.to_datetime(
            series,
            errors="coerce"
        )

        is_date_column = (
            date_series.notna().mean() >= 0.8
        )

        # -----------------------------------
        # Sample Values
        # -----------------------------------

        sample_values = (
            series
            .dropna()
            .astype(str)
            .unique()
            [:10]
            .tolist()
        )

        sample_text = ", ".join(
            sample_values
        )

        # -----------------------------------
        # Statistics
        # -----------------------------------

        if is_date_column:

            valid_dates = date_series.dropna()

            statistics = f"""
This column contains date values.

Minimum date: {valid_dates.min().date()}
Maximum date: {valid_dates.max().date()}
"""

        elif pd.api.types.is_numeric_dtype(series):

            statistics = f"""
Minimum value: {series.min()}
Maximum value: {series.max()}
Average value: {series.mean():.2f}
"""

        else:

            unique_count = series.nunique()

            statistics = f"""
Number of unique values: {unique_count}
"""

        # -----------------------------------
        # Business Meaning
        # -----------------------------------

        column_name = column.lower()

        if column_name == "sales":

            business_meaning = """
Business meaning:
Sales, revenue, sales amount, total sales,
money generated from sales.
"""

        elif column_name == "profit":

            business_meaning = """
Business meaning:
Profit, earnings, profit amount,
money earned after costs.
"""

        elif column_name == "quantity":

            business_meaning = """
Business meaning:
Quantity, units sold, number of items,
number of products sold.
"""

        elif "product" in column_name:

            business_meaning = """
Business meaning:
Product, item, merchandise, goods.
"""

        elif "customer" in column_name:

            business_meaning = """
Business meaning:
Customer, buyer, client.
"""

        elif "region" in column_name:

            business_meaning = """
Business meaning:
Region, geographical area, territory.
"""

        elif "category" in column_name:

            business_meaning = """
Business meaning:
Category, product group, product type.
"""

        elif "date" in column_name:

            business_meaning = """
Business meaning:
Date, time period, order date,
transaction date.
"""

        else:

            business_meaning = f"""
Business meaning:
{column.replace("_", " ")}.
"""

        # -----------------------------------
        # Column Description
        # -----------------------------------

        column_description = f"""
Table: {table_name}

Column: {column}

Data type: {dtype}

{business_meaning}

Sample values:
{sample_text}

{statistics}

This column can be used when answering questions related to
{column.replace("_", " ")}.

Values that may appear in this column include:
{sample_text}
"""

        documents.append(
            Document(
                page_content=column_description,
                metadata={
                    "type": "column",
                    "table": table_name,
                    "column": column
                }
            )
        )

    return documents


# -----------------------------------
# Create Vector Store
# -----------------------------------

def create_schema_vector_store(
    df,
    table_name
):

    documents = create_schema_documents(
        df,
        table_name
    )

    embeddings = get_embeddings()

    vector_store = FAISS.from_documents(
        documents,
        embeddings
    )

    return vector_store


# -----------------------------------
# Normalize Text
# -----------------------------------

def normalize_text(text):

    return (
        str(text)
        .lower()
        .replace("?", " ")
        .replace(",", " ")
        .replace(".", " ")
        .replace("(", " ")
        .replace(")", " ")
        .replace("-", " ")
        .replace("_", " ")
    )


# -----------------------------------
# Check Column Relevance
# -----------------------------------

def check_column_relevance(
    question,
    column_names
):

    question_words = set(
        normalize_text(question).split()
    )

    for column in column_names:

        column_words = (
            normalize_text(column)
            .split()
        )

        for word in question_words:

            for column_word in column_words:

                if (
                    len(word) >= 3
                    and (
                        word == column_word
                        or word in column_word
                        or column_word in word
                    )
                ):

                    return True

    return False


# -----------------------------------
# Check Business Terms
# -----------------------------------

def check_business_relevance(question):

    question_words = set(
        normalize_text(question).split()
    )

    business_terms = {
        "sales",
        "sale",
        "revenue",
        "profit",
        "earnings",
        "quantity",
        "units",
        "product",
        "products",
        "customer",
        "customers",
        "buyer",
        "buyers",
        "client",
        "clients",
        "order",
        "orders",
        "category",
        "categories",
        "region",
        "regions",
        "city",
        "cities",
        "state",
        "states",
        "country",
        "countries",
        "discount",
        "discounts",
        "shipping",
        "shipment",
        "shipments",
        "date",
        "dates",
        "time",
        "month",
        "months",
        "year",
        "years",
        "trend",
        "trends",
        "average",
        "total",
        "highest",
        "lowest",
        "maximum",
        "minimum",
        "top",
        "bottom",
        "count",
        "number",
    }

    return bool(
        question_words.intersection(
            business_terms
        )
    )


# -----------------------------------
# Check Dataset Values
# -----------------------------------

def check_value_relevance(
    question,
    df
):
    """
    Check whether the question contains
    a value that exists in the dataset.
    """

    question_lower = normalize_text(
        question
    )

    for column in df.columns:

        series = df[column]

        # Check only text-like columns
        if not (
            pd.api.types.is_object_dtype(series)
            or pd.api.types.is_string_dtype(series)
        ):
            continue

        values = (
            series
            .dropna()
            .astype(str)
            .str.lower()
            .unique()
        )

        for value in values:

            value = normalize_text(
                value
            ).strip()

            if len(value) < 3:
                continue

            if value in question_lower:

                return True

    return False


# -----------------------------------
# Retrieve Relevant Schema
# -----------------------------------

def retrieve_schema(
    vector_store,
    question,
    df,
    k=6
):
    """
    Retrieve relevant schema information.

    Uses:

    1. Semantic similarity
    2. Column matching
    3. Business terminology
    4. Dataset-value matching

    Completely unrelated questions are rejected
    before SQL generation.
    """

    # -----------------------------------
    # Retrieve Candidates
    # -----------------------------------

    results = (
        vector_store
        .similarity_search_with_score(
            question,
            k=k
        )
    )

    # -----------------------------------
    # Get All Dataset Columns
    # -----------------------------------

    column_names = [
        column.lower()
        for column in df.columns
    ]

    # -----------------------------------
    # Column Relevance
    # -----------------------------------

    column_relevant = check_column_relevance(
        question,
        column_names
    )

    # -----------------------------------
    # Business Relevance
    # -----------------------------------

    business_relevant = check_business_relevance(
        question
    )

    # -----------------------------------
    # Dataset Value Relevance
    # -----------------------------------

    value_relevant = check_value_relevance(
        question,
        df
    )

    # -----------------------------------
    # Semantic Relevance
    # -----------------------------------

    semantic_relevant = False

    for document, score in results:

        if score <= 1.8:

            semantic_relevant = True

            break

    # -----------------------------------
    # Final Relevance
    # -----------------------------------

    relevant = (
        column_relevant
        or business_relevant
        or value_relevant
        or semantic_relevant
    )

    # -----------------------------------
    # Reject Unrelated Questions
    # -----------------------------------

    if not relevant:

        return ""

    # -----------------------------------
    # Build Schema
    # -----------------------------------

    schema_parts = []

    for document, score in results:

        if score <= 1.8:

            schema_parts.append(
                document.page_content
            )

    return "\n\n".join(
        schema_parts
    )