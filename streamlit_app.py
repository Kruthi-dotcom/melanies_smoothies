# Import required packages
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Set the page title
st.set_page_config(page_title="Smoothie Customizer", page_icon="🍓")

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
    '🍓 Choose up to 5 fresh ingredients:',
    pd_df['FRUIT_NAME'].tolist(),
    max_selections=5
)

# If fruits are selected, show nutrition info and build the order
if ingredients_list:
    ingredients_string = ", ".join(ingredients_list)

    # Display order preview
    st.markdown("### 📝 Order Preview")
    st.write(f"**Name:** {name_on_order}")
    st.write(f"**Ingredients:** {ingredients_string}")

    # Show nutrition info for each selected fruit
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        st.subheader(f'{fruit_chosen} Nutrition Information')
        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if smoothiefroot_response.status_code == 200:
            st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)
        else:
            st.error(f"❌ Failed to fetch nutrition info for {fruit_chosen}.")

    # Submit order button
    if st.button('Submit Order'):
        if name_on_order.strip() == "":
            st.warning("⚠️ Please enter a name before submitting your order.")
        else:
            # Insert into Snowflake with status PENDING
            session.sql(
                "INSERT INTO smoothies.public.orders (ingredients, name_on_order, filled_status) VALUES (?, ?, ?)",
                (ingredients_string, name_on_order, 'PENDING')
            ).collect()
            st.success(f'✅ Your Smoothie is ordered, {name_on_order}!')
else:
    st.info("Please choose your smoothie ingredients to continue.")

