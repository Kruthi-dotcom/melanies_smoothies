# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

# User input for name
name_on_order = st.text_input('Name on Smoothie: ')
st.write("The name on your Smoothie will be: ", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Fruit selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)  # Cleaned string format

    # Display nutrition information
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.write(f'The search value for {fruit_chosen} is {search_on}.')
        st.subheader(f'{fruit_chosen} Nutrition Information')

        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")

    # Submit order button
    if st.button('Submit Order'):
        session.sql("INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)", 
                    (ingredients_string, name_on_order)).collect()
        st.success(f'Your Smoothie is ordered, {name_on_order}!', icon="✅")
