# Import necessary packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Streamlit App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()

# Convert fruit names to a list for the dropdown
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multi-select for ingredients (Allow up to 5)
ingredients_list = st.multiselect('Choose up to 5 ingredients:', fruit_list, max_selections=5)

if ingredients_list:
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        if search_on:  # Ensure there's a valid search value
            st.subheader(f"{fruit_chosen} Nutrition Information")

            try:
                fruityvice_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                if fruityvice_response.status_code == 200:
                    nutrition_data = fruityvice_response.json()
                    st.table(nutrition_data)  # Display response as table
                else:
                    st.write(f"Could not fetch data for {fruit_chosen}.")
            except Exception as e:
                st.write(f"Error fetching data: {e}")

# Button to submit order (Handled manually via SQL insert)
st.button('Submit Order')
