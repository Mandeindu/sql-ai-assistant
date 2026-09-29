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


# -----------------------------------
# Create RAG
# -----------------------------------

print("\nCreating RAG...")

vector_store = create_schema_vector_store(
    df,
    table_name
)

print("RAG created successfully!")


# -----------------------------------
# Conversation History
# -----------------------------------

history = []


# ===================================
# QUESTION 1
# ===================================

question1 = "What are the top 5 products by sales?"

print("\n" + "=" * 60)

print("QUESTION 1:")
print(question1)


response1 = ask_database(
    question1,
    vector_store,
    database_path,
    table_name,
    history
)


if response1["success"]:

    print("\nGenerated SQL:")
    print(response1["sql"])

    print("\nResult:")
    print(response1["result"])

    # Save conversation
    history.append({
        "question": question1,
        "sql": response1["sql"],
        "result": response1["result"].to_string(index=False)
    })

else:

    print("\nError:")
    print(response1["error"])


# ===================================
# QUESTION 2
# ===================================

question2 = "What about their profit?"

print("\n" + "=" * 60)

print("QUESTION 2:")
print(question2)


response2 = ask_database(
    question2,
    vector_store,
    database_path,
    table_name,
    history
)


if response2["success"]:

    print("\nGenerated SQL:")
    print(response2["sql"])

    print("\nResult:")
    print(response2["result"])

else:

    print("\nError:")
    print(response2["error"])