# Import necessary packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Streamlit App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# User Input for Smoothie Name (No extra display)
name_on_order = st.text_input('Enter the Name for Your Smoothie:', '')

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()  # Convert Snowflake DataFrame to Pandas

# Display Available Fruits
st.dataframe(pd_df)

# Convert fruit names to a list for the dropdown
fruit_list = pd_df['FRUIT_NAME'].tolist()

# Multi-select for ingredients (Choose up to 5)
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:', fruit_list, max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Join selected ingredients into a string

    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        if search_on:  # Ensure there's a valid search value
            st.subheader(f"{fruit_chosen} Nutrition Information")
            try:
                fruityvice_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
                if fruityvice_response.status_code == 200:
                    st.json(fruityvice_response.json())  # Display API response
                else:
                    st.write(f"Could not fetch data for {fruit_chosen}.")
            except Exception as e:
                st.write(f"Error fetching data: {e}")

    # Ensure name_on_order is not empty before inserting into Snowflake
    if name_on_order.strip():
        my_insert_stmt = f"""
            INSERT INTO smoothies.public.orders (ingredients, name_on_order)
            VALUES ('{ingredients_string}', '{name_on_order}')
        """

        # Button to submit order
        if st.button('Submit Order'):
            session.sql(my_insert_stmt).collect()
            st.success(f'Your Smoothie is ordered! 🎉', icon="✅")
    else:
        st.error("Please enter a name for your Smoothie before submitting.")
