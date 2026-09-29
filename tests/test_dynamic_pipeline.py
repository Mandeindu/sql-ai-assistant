from dataset_manager import load_dataset

from schema_rag import create_schema_vector_store

from pipeline import ask_database


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

print("Database:", database_path)

print("Table:", table_name)


# -----------------------------------
# Create Dynamic RAG
# -----------------------------------

print("\nCreating RAG...")

vector_store = create_schema_vector_store(
    df,
    table_name
)

print("RAG created successfully!")


# -----------------------------------
# Ask Question
# -----------------------------------

question = "What are the top 10 products by profit?"


print("\nUser Question:")
print(question)


# -----------------------------------
# Run Complete Pipeline
# -----------------------------------

print("\nRunning AI pipeline...")

response = ask_database(
    question,
    vector_store,
    database_path,
    table_name
)


# -----------------------------------
# Show Result
# -----------------------------------

if response["success"]:

    print("\n✅ Query executed successfully!")

    print("\nGenerated SQL:")
    print(response["sql"])

    print("\nQuery Result:")
    print(response["result"])

    if response["corrected"]:

        print("\n🔧 SQL was automatically corrected.")

else:

    print("\n❌ Query failed.")

    print("\nSQL:")
    print(response["sql"])

    print("\nError:")
    print(response["error"])