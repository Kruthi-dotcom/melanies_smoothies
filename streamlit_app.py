# Import required libraries
import streamlit as st
from snowflake.snowpark.functions import col
import requests
import pandas as pd

# Streamlit App Title
st.title(":cup_with_straw: Customize Your Smoothie! :cup_with_straw:")
st.write("Choose the fruits you want in your custom smoothie")

# User Input for Name on Order
name_on_order = st.text_input('Name on Smoothie:')
st.write("The name on your Smoothie will be:", name_on_order)

# Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Retrieve Fruit Options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).to_pandas()

# Display Fruit Selection
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    my_dataframe['FRUIT_NAME'].tolist(),  # List of available fruits
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Create ingredient string

    for fruit_chosen in ingredients_list:
        search_result = my_dataframe.loc[my_dataframe['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON']

        if not search_result.empty:
            search_on = search_result.iloc[0]

            # Display Search Value
            st.write(f"The search value for {fruit_chosen} is {search_on}.")

            # Fetch Nutrition Information if valid
            if pd.notna(search_on) and isinstance(search_on, str) and search_on.strip():
                st.subheader(f"{fruit_chosen} Nutrition Information")

                try:
                    api_url = f"https://my.smoothiefroot.com/api/fruit/{search_on}"
                    response = requests.get(api_url)
                    response.raise_for_status()  # Raise error if request fails

                    nutrition_data = response.json()
                    st.dataframe(nutrition_data, use_container_width=True)

                except requests.exceptions.RequestException as e:
                    st.error(f"Failed to retrieve nutrition info for {fruit_chosen}: {e}")
            else:
                st.warning(f"No valid search value found for {fruit_chosen}. Cannot fetch nutrition info.")
        else:
            st.error(f"Could not find {fruit_chosen} in the dataset.")

    # Insert Order into Database
    insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    # Submit Order Button
    if st.button('Submit Order'):
        session.sql(insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")

