# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write(
    """Choose the fruits you want in your custom Smoothie!
    """
)

# Feature: Capture the customer's name
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Feature: New Connection Method
cnx = st.connection("snowflake")
session = cnx.session()

# Load fruit options and convert to a format Streamlit understands
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'))

# Convert the Snowpark dataframe to a Pandas dataframe so the list displays correctly
pd_df = my_dataframe.to_pandas()

# Feature: Multiselect with a maximum of 5 choices
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:'
    , pd_df['FRUIT_NAME'] # Use the specific column from the Pandas dataframe
    , max_selections=5
)

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

    # Feature: SQL Insert including ingredients AND customer name
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients, name_on_order)
            values ('""" + ingredients_string + """','""" + name_on_order + """')"""

    # Optional Troubleshooting: Uncomment the next two lines to check SQL before submitting
    # st.write(my_insert_stmt)
    # st.stop()

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
