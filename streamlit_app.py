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

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom Smoothie!")

_name_on_order = st.text_input("Name in smoothie:")
st.write("The name on your smoothie will be:", _name_on_order)

# ✅ Universal session
session = get_snowflake_session()

my_dataframe = session.table("SMOOTHIES.PUBLIC.FRUIT_OPTIONS").select(col("FRUIT_NAME"), col('SEARCH_ON'))

# st.dataframe(data=my_dataframe, use_container_width=True)
# st.stop()

pd_df = my_dataframe.to_pandas()
#st.dataframe(pd_df)
#st.stop()

ingredients_list = st.multiselect(
    "Choose up to 5 ingredients:",
    my_dataframe.to_pandas()["FRUIT_NAME"].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = " ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write('The search value for ', fruit_chosen,' is ', search_on, '.')
        
        st.subheader(fruit_chosen + 'Nutrition Information')
        fruityvice_response = requests.get("https://my.fruityvice.com/api/fruit/" + fruit_chosen)
        
        #smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + fruit_chosen)
        # st.text(smoothiefroot_response)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        
    if st.button("Submit Order"):
        session.sql(
            "INSERT INTO SMOOTHIES.PUBLIC.ORDERS (ingredients, name_on_order) VALUES (?, ?)",
            params=[ingredients_string, _name_on_order]
        ).collect()

        st.success("Your Smoothie is ordered!", icon="✅")
