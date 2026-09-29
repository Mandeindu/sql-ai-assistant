import pandas as pd


def generate_insights(question, result):
    """
    Generate concise insights from SQL query results.
    """

    if result is None or result.empty:

        return "No data was returned for this question."


    insights = []


    # -----------------------------------
    # Identify Numeric Columns
    # -----------------------------------

    numeric_columns = result.select_dtypes(
        include=["number"]
    ).columns.tolist()


    # -----------------------------------
    # No Numeric Columns
    # -----------------------------------

    if not numeric_columns:

        insights.append(
            f"• The result contains {len(result)} record(s)."
        )

        return "\n".join(insights)


    # -----------------------------------
    # Generate Insights
    # -----------------------------------

    for column in numeric_columns[:2]:

        series = result[column].dropna()


        if series.empty:

            continue


        highest = series.max()
        lowest = series.min()


        highest_index = series.idxmax()
        lowest_index = series.idxmin()


        # -----------------------------------
        # Find Label Column
        # -----------------------------------

        label_columns = [
            col
            for col in result.columns
            if col != column
        ]


        if label_columns:

            label_column = label_columns[0]


            highest_label = result.loc[
                highest_index,
                label_column
            ]


            lowest_label = result.loc[
                lowest_index,
                label_column
            ]


            # -----------------------------------
            # Avoid Duplicate Highest/Lowest
            # -----------------------------------

            if highest == lowest:

                insights.append(
                    f"• {column}: "
                    f"{highest:,.2f}"
                )

            else:

                insights.append(
                    f"• Highest {column}: "
                    f"{highest_label} "
                    f"({highest:,.2f})"
                )

                insights.append(
                    f"• Lowest {column}: "
                    f"{lowest_label} "
                    f"({lowest:,.2f})"
                )


        else:

            if highest == lowest:

                insights.append(
                    f"• {column}: "
                    f"{highest:,.2f}"
                )

            else:

                insights.append(
                    f"• Highest {column}: "
                    f"{highest:,.2f}"
                )

                insights.append(
                    f"• Lowest {column}: "
                    f"{lowest:,.2f}"
                )


    # -----------------------------------
    # Result Count
    # -----------------------------------

    insights.append(
        f"• The result contains "
        f"{len(result)} record(s)."
    )


    # -----------------------------------
    # Return Maximum 4 Insights
    # -----------------------------------

    return "\n".join(
        insights[:4]
    )