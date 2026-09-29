from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# Load the same embedding model
embeddings = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)


# Load the saved FAISS index
vector_store = FAISS.load_local(
    "faiss_index",
    embeddings,
    allow_dangerous_deserialization=True
)


# Example user question
question = "Which columns contain information about profit and sales?"


# Retrieve relevant schema
results = vector_store.similarity_search(
    question,
    k=1
)


print("\nUser Question:")
print(question)

print("\nRetrieved Schema:")
print(results[0].page_content)