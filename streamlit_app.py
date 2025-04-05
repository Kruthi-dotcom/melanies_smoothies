# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Title and description
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

# User input for name
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be: ", name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Fruit selection
ingredients_list = st.multiselect(
    '🍓 Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# Display nutrition info for selected fruits
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f'{fruit_chosen} Nutrition Information')

        response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
        if response.status_code == 200:
            st.dataframe(data=response.json(), use_container_width=True)
        else:
            st.error(f"Failed to fetch nutrition info for {fruit_chosen}.")

    # Order Preview
    st.markdown("### 🧾 Order Preview")
    st.write(f"**Name:** {name_on_order}")
    st.write(f"**Ingredients:** {ingredients_string}")
    st.write(f"**Order Status:** Not Filled")

    # Submit button
    if st.button('Submit Order'):
        if name_on_order.strip() == "":
            st.warning("Please enter a name before submitting your order.")
        else:
            # Insert into Snowflake with order_filled = False
            session.sql("""
                INSERT INTO smoothies.public.orders (order_filled, name_on_order, ingredients)
                VALUES (?, ?, ?)
            """, (False, name_on_order, ingredients_string)).collect()

            st.success(f'Your Smoothie is ordered, {name_on_order}! 🍹', icon="✅")
