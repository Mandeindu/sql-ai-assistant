from dataset_manager import load_dataset
from schema_rag import (
    create_schema_vector_store,
    retrieve_schema
)


DATASET_PATH = "Sample - Superstore.csv"


# Read the dataset
with open(DATASET_PATH, "rb") as file:
    file_bytes = file.read()


# Load dataset
df, database_path, table_name = load_dataset(
    DATASET_PATH,
    file_bytes
)


print("\nDataset loaded successfully!")

print("Table:", table_name)

print("Rows:", len(df))

print("Columns:", len(df.columns))


# Create dynamic RAG
print("\nCreating schema RAG...")

vector_store = create_schema_vector_store(
    df,
    table_name
)

print("Schema RAG created successfully!")


# Test questions
questions = [
    "What are the top products by profit?",
    "Which region has the highest sales?",
    "What is the average discount?"
]


for question in questions:

    print("\n" + "=" * 60)

    print("Question:")
    print(question)

    print("\nRetrieved Schema:")

    schema = retrieve_schema(
        vector_store,
        question,
        k=6
    )

    print(schema)