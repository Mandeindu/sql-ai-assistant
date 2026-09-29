from dataset_manager import load_dataset

from schema_rag import (
    create_schema_vector_store,
    retrieve_schema
)

from sql_generator import generate_sql


DATASET_PATH = "Sample - Superstore.csv"


# -----------------------------------
# Load Dataset
# -----------------------------------

with open(DATASET_PATH, "rb") as file:
    file_bytes = file.read()


df, database_path, table_name = load_dataset(
    DATASET_PATH,
    file_bytes
)


print("\nDataset loaded successfully!")

print("Table:", table_name)


# -----------------------------------
# Create Dynamic RAG
# -----------------------------------

print("\nCreating schema RAG...")

vector_store = create_schema_vector_store(
    df,
    table_name
)

print("Schema RAG created successfully!")


# -----------------------------------
# Ask Question
# -----------------------------------

question = "What are the top 10 products by profit?"


print("\nUser Question:")
print(question)


# -----------------------------------
# Retrieve Relevant Schema
# -----------------------------------

schema = retrieve_schema(
    vector_store,
    question,
    k=6
)


print("\nRelevant Schema:")
print(schema)


# -----------------------------------
# Generate SQL
# -----------------------------------

print("\nGenerating SQL using Qwen...")


sql = generate_sql(
    question,
    schema,
    table_name
)


print("\nGenerated SQL:")
print(sql)