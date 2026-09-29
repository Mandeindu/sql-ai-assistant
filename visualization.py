import pandas as pd
import plotly.express as px


def create_chart(df):
    """
    Automatically create a suitable chart
    from SQL query results.
    """

    if df is None or df.empty:
        return None

    # A chart needs at least two columns
    if df.shape[1] < 2:
        return None

    columns = df.columns.tolist()


    # -----------------------------------
    # Identify Numeric Columns
    # -----------------------------------

    numeric_columns = df.select_dtypes(
        include=["number"]
    ).columns.tolist()


    # -----------------------------------
    # Identify Categorical Columns
    # -----------------------------------

    categorical_columns = [
        column
        for column in columns
        if column not in numeric_columns
    ]


    # -----------------------------------
    # No Numeric Data
    # -----------------------------------

    if not numeric_columns:
        return None


    # -----------------------------------
    # One Categorical + One Numeric
    # -----------------------------------

    if (
        len(numeric_columns) == 1
        and categorical_columns
    ):

        x_column = categorical_columns[0]
        y_column = numeric_columns[0]


        # -----------------------------------
        # Detect Time-Series Columns
        # -----------------------------------

        time_keywords = [
            "date",
            "time",
            "month",
            "year",
            "quarter",
            "week"
        ]

        is_time_column = any(
            keyword in x_column.lower()
            for keyword in time_keywords
        )


        # -----------------------------------
        # Time-Series → Line Chart
        # -----------------------------------

        if is_time_column:

            chart_df = df.copy()


            # Try to convert to datetime
            parsed_dates = pd.to_datetime(
                chart_df[x_column],
                errors="coerce"
            )


            if parsed_dates.notna().mean() >= 0.8:

                chart_df["_parsed_time"] = parsed_dates

                chart_df = chart_df.sort_values(
                    "_parsed_time"
                )

                fig = px.line(
                    chart_df,
                    x=x_column,
                    y=y_column,
                    markers=True,
                    title=f"{y_column} over time"
                )

                return fig


            # -----------------------------------
            # Handle YYYY-MM / YYYY values
            # -----------------------------------

            chart_df = chart_df.sort_values(
                x_column
            )

            fig = px.line(
                chart_df,
                x=x_column,
                y=y_column,
                markers=True,
                title=f"{y_column} over time"
            )

            return fig


        # -----------------------------------
        # Small Number of Categories
        # → Bar Chart
        # -----------------------------------

        if df[x_column].nunique() <= 15:

            fig = px.bar(
                df,
                x=x_column,
                y=y_column,
                title=f"{y_column} by {x_column}"
            )

            return fig


        # -----------------------------------
        # Many Categories
        # → Horizontal Bar Chart
        # -----------------------------------

        fig = px.bar(
            df,
            x=y_column,
            y=x_column,
            orientation="h",
            title=f"{y_column} by {x_column}"
        )

        return fig


    # -----------------------------------
    # Multiple Numeric + Categorical
    # -----------------------------------

    if (
        len(numeric_columns) >= 2
        and categorical_columns
    ):

        x_column = categorical_columns[0]

        y_columns = numeric_columns[:2]


        chart_data = df[
            [x_column] + y_columns
        ]


        chart_data = chart_data.melt(
            id_vars=x_column,
            value_vars=y_columns,
            var_name="Metric",
            value_name="Value"
        )


        fig = px.bar(
            chart_data,
            x=x_column,
            y="Value",
            color="Metric",
            barmode="group",
            title=f"Comparison by {x_column}"
        )

        return fig


    # -----------------------------------
    # Two Numeric Columns
    # → Scatter Plot
    # -----------------------------------

    if len(numeric_columns) == 2:

        x_column = numeric_columns[0]
        y_column = numeric_columns[1]


        fig = px.scatter(
            df,
            x=x_column,
            y=y_column,
            title=f"{y_column} vs {x_column}"
        )

        return fig


    # -----------------------------------
    # No Suitable Chart
    # -----------------------------------

    return None