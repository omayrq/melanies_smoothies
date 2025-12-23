# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Capture the customer's name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connection Method for Streamlit Cloud
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options and convert to Pandas for the widget
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))
pd_df = my_dataframe.to_pandas()

# Multiselect with a maximum of 5 choices
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , pd_df['FRUIT_NAME']
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
        
        # New section to display smoothiefroot nutrition information
        st.subheader(fruit_chosen + ' Nutrition Information')
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/watermelon")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        #st.text(smoothiefroot_response.json())
    
    # SQL Insert statement
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
