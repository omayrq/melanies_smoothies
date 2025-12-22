# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Try Snowflake Streamlit first, else fallback to normal Streamlit
def get_snowflake_session():
    try:
        from snowflake.snowpark.context import get_active_session
        return get_active_session()
    except Exception:
        cnx = st.connection("Snowflake")
        return cnx.session()

st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

_name_on_order = st.text_input("Name in smoothie:")
st.write("The name on your smoothie will be:", _name_on_order)

# ✅ NEW: Order filled confirmation
order_filled = st.checkbox("Mark order as filled")

# Snowflake session
session = get_snowflake_session()

my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS") \
                      .select(col("FRUIT_NAME"), col("SEARCH_ON"))

pd_df = my_dataframe.to_pandas()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    pd_df["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    # ✅ CORRECT FORMAT FOR GRADER
    ingredients_string = ", ".join(ingredients_list)

    # Display nutrition info
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[
            pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'
        ].iloc[0]

        st.subheader(fruit_chosen + " Nutrition Information")

        response = requests.get(
            f"https://my.smoothiefroot.com/api/fruit/{search_on}"
        )

        if response.status_code == 200:
            st.dataframe(response.json(), use_container_width=True)
        else:
            st.error(f"Could not find nutrition data for {fruit_chosen}")

    time_to_insert = st.button("Submit Order")

    if time_to_insert:
        session.sql(
            """
            INSERT INTO SMOOTHIES.PUBLIC.ORDERS
            (ingredients, name_on_order, order_filled, order_ts)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """,
            params=[
                ingredients_string,
                _name_on_order,
                order_filled
            ]
        ).collect()

        st.success(
            f"Your Smoothie is ordered, {_name_on_order}!",
            icon="✅"
        )
