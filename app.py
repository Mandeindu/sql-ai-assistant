import streamlit as st

from dataset_manager import load_dataset
from schema_rag import create_schema_vector_store
from pipeline import ask_database


# -----------------------------------
# Configuration
# -----------------------------------

MAX_DISPLAY_ROWS = 100


# -----------------------------------
# Page Configuration
# -----------------------------------

st.set_page_config(
    page_title="SQL AI Assistant",
    page_icon="🤖",
    layout="wide"
)


# -----------------------------------
# Session State
# -----------------------------------

if "history" not in st.session_state:
    st.session_state["history"] = []

if "selected_question" not in st.session_state:
    st.session_state["selected_question"] = None


# -----------------------------------
# Sidebar
# -----------------------------------

with st.sidebar:

    st.header("💬 Conversation")

    if st.session_state["history"]:

        st.write(
            f"{len(st.session_state['history'])} "
            "question(s) asked"
        )

        for index, item in enumerate(
            st.session_state["history"],
            start=1
        ):

            st.write(
                f"**{index}.** {item['question']}"
            )

    else:

        st.write(
            "No questions asked yet."
        )


# -----------------------------------
# Title
# -----------------------------------

st.title("🤖 SQL AI Assistant")

st.write(
    "Upload a CSV or Excel dataset and ask questions "
    "using natural language."
)


# -----------------------------------
# Upload Dataset
# -----------------------------------

st.subheader("📂 Upload Your Dataset")

uploaded_file = st.file_uploader(
    "Choose a CSV or Excel file",
    type=["csv", "xlsx", "xls"]
)


# -----------------------------------
# Process Dataset
# -----------------------------------

if uploaded_file is not None:

    file_id = (
        f"{uploaded_file.name}_{uploaded_file.size}"
    )

    # Process only when a new file is uploaded
    if st.session_state.get("file_id") != file_id:

        try:

            with st.spinner(
                "⏳ Processing your dataset... "
                "This may take a moment."
            ):

                file_bytes = uploaded_file.getvalue()

                # -----------------------------------
                # Create SQLite Database
                # -----------------------------------

                df, database_path, table_name = load_dataset(
                    uploaded_file.name,
                    file_bytes
                )

                st.toast(
                    "✅ Database created"
                )

                # -----------------------------------
                # Create RAG Vector Store
                # -----------------------------------

                vector_store = create_schema_vector_store(
                    df,
                    table_name
                )

                st.toast(
                    "✅ Dataset schema indexed"
                )

                # -----------------------------------
                # Clear Previous Dataset
                # -----------------------------------

                st.session_state.pop(
                    "dataframe",
                    None
                )

                st.session_state.pop(
                    "database_path",
                    None
                )

                st.session_state.pop(
                    "table_name",
                    None
                )

                st.session_state.pop(
                    "vector_store",
                    None
                )

                # Reset conversation
                st.session_state["history"] = []

                # Reset sample question
                st.session_state[
                    "selected_question"
                ] = None

                # -----------------------------------
                # Store New Dataset
                # -----------------------------------

                st.session_state["file_id"] = file_id

                st.session_state["dataframe"] = df

                st.session_state[
                    "database_path"
                ] = database_path

                st.session_state[
                    "table_name"
                ] = table_name

                st.session_state[
                    "vector_store"
                ] = vector_store

            st.success(
                "✅ Dataset uploaded and AI database created!"
            )

        except Exception as e:

            st.error(
                "❌ Could not process the dataset."
            )

            st.exception(e)


# -----------------------------------
# Dataset Information
# -----------------------------------

if "dataframe" in st.session_state:

    df = st.session_state["dataframe"]

    st.subheader(
        "📊 Dataset Information"
    )

    col1, col2, col3 = st.columns(3)

    with col1:

        st.metric(
            "Rows",
            df.shape[0]
        )

    with col2:

        st.metric(
            "Columns",
            df.shape[1]
        )

    with col3:

        st.metric(
            "Database",
            "SQLite"
        )


    # -----------------------------------
    # Dataset Preview
    # -----------------------------------

    st.subheader(
        "👀 Dataset Preview"
    )

    st.dataframe(
        df.head(10),
        width="stretch"
    )


    # -----------------------------------
    # Dataset Columns
    # -----------------------------------

    with st.expander(
        "📋 View Dataset Columns"
    ):

        st.write(
            ", ".join(df.columns)
        )


    # -----------------------------------
    # Database Information
    # -----------------------------------

    with st.expander(
        "🗄️ Database Information"
    ):

        st.write(
            f"Table: "
            f"`{st.session_state['table_name']}`"
        )

        st.write(
            f"Database: "
            f"`{st.session_state['database_path']}`"
        )


    # -----------------------------------
    # Chat Interface
    # -----------------------------------

    st.subheader(
        "💬 Chat with Your Dataset"
    )


    # -----------------------------------
    # Sample Questions
    # -----------------------------------

    st.write(
        "Try asking:"
    )

    sample_questions = [
        "What are the top 5 products by sales?",
        "Which category has the highest profit?",
        "Which region has the highest sales?",
        "What is the total quantity sold?"
    ]

    sample_cols = st.columns(4)

    for index, sample_question in enumerate(
        sample_questions
    ):

        with sample_cols[index]:

            if st.button(
                sample_question,
                key=f"sample_question_{index}"
            ):

                st.session_state[
                    "selected_question"
                ] = sample_question

                st.rerun()


    # -----------------------------------
    # Clear Chat
    # -----------------------------------

    if st.button(
        "🗑️ Clear Chat"
    ):

        st.session_state["history"] = []

        st.session_state[
            "selected_question"
        ] = None

        st.rerun()


    # -----------------------------------
    # Display Previous Conversations
    # -----------------------------------

    for index, item in enumerate(
        st.session_state["history"],
        start=1
    ):

        with st.chat_message("user"):

            st.write(
                item["question"]
            )


        with st.chat_message("assistant"):

            # -----------------------------------
            # Generated SQL
            # -----------------------------------

            if item.get("sql"):

                with st.expander(
                    "🔍 View Generated SQL"
                ):

                    st.code(
                        item["sql"],
                        language="sql"
                    )


            # -----------------------------------
            # Query Result
            # -----------------------------------

            if item.get("result") is not None:

                st.subheader(
                    "📊 Query Results"
                )

                result_to_display = (
                    item["result"]
                    .head(MAX_DISPLAY_ROWS)
                )

                st.dataframe(
                    result_to_display,
                    width="stretch"
                )


                if len(item["result"]) > MAX_DISPLAY_ROWS:

                    st.caption(
                        f"Showing first "
                        f"{MAX_DISPLAY_ROWS} rows "
                        f"of {len(item['result'])} "
                        "total rows. "
                        "Download the CSV to view "
                        "all results."
                    )


                # -----------------------------------
                # Download Previous Result
                # -----------------------------------

                csv_data = (
                    item["result"]
                    .to_csv(index=False)
                )

                st.download_button(
                    label="⬇️ Download Results",
                    data=csv_data,
                    file_name=(
                        f"query_results_{index}.csv"
                    ),
                    mime="text/csv",
                    key=f"download_previous_{index}"
                )


            # -----------------------------------
            # Visualization
            # -----------------------------------

            if item.get("chart") is not None:

                st.subheader(
                    "📈 Visualization"
                )

                st.plotly_chart(
                    item["chart"],
                    width="stretch"
                )


            # -----------------------------------
            # Data Insights
            # -----------------------------------

            if item.get("insights"):

                st.subheader(
                    "💡 Data Insights"
                )

                st.markdown(
                    item["insights"].replace(
                        "\n",
                        "  \n"
                    )
                )


    # -----------------------------------
    # New Question
    # -----------------------------------

    question = st.chat_input(
        "Ask a question about your dataset..."
    )


    # -----------------------------------
    # Check Sample Question
    # -----------------------------------

    if st.session_state[
        "selected_question"
    ]:

        question = st.session_state[
            "selected_question"
        ]

        st.session_state[
            "selected_question"
        ] = None


    # -----------------------------------
    # Process Question
    # -----------------------------------

    if question:

        # -----------------------------------
        # Display User Question
        # -----------------------------------

        with st.chat_message("user"):

            st.write(
                question
            )


        # -----------------------------------
        # Generate AI Response
        # -----------------------------------

        with st.chat_message("assistant"):

            with st.spinner(
                "🔎 Analyzing your question..."
            ):

                response = ask_database(
                    question,
                    st.session_state[
                        "vector_store"
                    ],
                    st.session_state[
                        "database_path"
                    ],
                    st.session_state[
                        "table_name"
                    ],
                    st.session_state[
                        "dataframe"
                    ],
                    st.session_state[
                        "history"
                    ]
                )


            # -----------------------------------
            # Successful Query
            # -----------------------------------

            if response["success"]:

                st.success(
                    "✅ Query executed successfully!"
                )


                # -----------------------------------
                # Save Conversation
                # -----------------------------------

                st.session_state[
                    "history"
                ].append({

                    "question": question,

                    "sql": response["sql"],

                    "result": response["result"],

                    "chart": response["chart"],

                    "insights": response["insights"]

                })


                # -----------------------------------
                # Generated SQL
                # -----------------------------------

                with st.expander(
                    "🔍 View Generated SQL"
                ):

                    st.code(
                        response["sql"],
                        language="sql"
                    )


                # -----------------------------------
                # SQL Correction Message
                # -----------------------------------

                if response["corrected"]:

                    st.info(
                        "🔧 The AI automatically corrected "
                        "an SQL error before executing "
                        "the query."
                    )


                # -----------------------------------
                # Query Results
                # -----------------------------------

                st.subheader(
                    "📊 Query Results"
                )

                result_to_display = (
                    response["result"]
                    .head(MAX_DISPLAY_ROWS)
                )

                st.dataframe(
                    result_to_display,
                    width="stretch"
                )


                if (
                    len(response["result"])
                    > MAX_DISPLAY_ROWS
                ):

                    st.caption(
                        f"Showing first "
                        f"{MAX_DISPLAY_ROWS} rows "
                        f"of {len(response['result'])} "
                        "total rows. "
                        "Download the CSV to view "
                        "all results."
                    )


                # -----------------------------------
                # Download Results
                # -----------------------------------

                csv_data = (
                    response["result"]
                    .to_csv(index=False)
                )

                st.download_button(
                    label="⬇️ Download Results",
                    data=csv_data,
                    file_name="query_results.csv",
                    mime="text/csv",
                    key="download_current_result"
                )


                # -----------------------------------
                # Visualization
                # -----------------------------------

                if response["chart"] is not None:

                    st.subheader(
                        "📈 Visualization"
                    )

                    st.plotly_chart(
                        response["chart"],
                        width="stretch"
                    )


                # -----------------------------------
                # Data Insights
                # -----------------------------------

                st.subheader(
                    "💡 Data Insights"
                )

                st.markdown(
                    response["insights"].replace(
                        "\n",
                        "  \n"
                    )
                )


            # -----------------------------------
            # Failed Query
            # -----------------------------------

            else:

                st.error(
                    "❌ Could not execute the query."
                )


                with st.expander(
                    "🔍 Generated SQL"
                ):

                    if response["sql"]:

                        st.code(
                            response["sql"],
                            language="sql"
                        )

                    else:

                        st.write(
                            "No SQL was generated."
                        )


                st.error(
                    response["error"]
                )