# Import required packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Streamlit App Title
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for user name on the smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Establish Snowflake Connection
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))
pd_df = my_dataframe.to_pandas()  # Convert to Pandas DataFrame
st.dataframe(pd_df)  # Display fruit options

st.stop()  # Stop execution to debug if needed

# Multi-select for choosing ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Convert DataFrame column to list
    max_selections=5
)

if ingredients_list:
    ingredients_string = ', '.join(ingredients_list)  # Create a comma-separated string of selected ingredients

    for fruit_chosen in ingredients_list:
        # Get the search term from the DataFrame
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display fruit nutrition information
        st.subheader(f"{fruit_chosen} Nutrition Information")

        # Fetch nutrition data from API
        try:
            response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")
            if response.status_code == 200:
                nutrition_data = response.json()
                st.write(nutrition_data)  # Display fetched data
            else:
                st.error(f"Could not fetch nutrition data for {fruit_chosen}.")
        except Exception as e:
            st.error(f"Error fetching data: {str(e)}")

    # SQL insert query (parameterized for security)
    my_insert_stmt = "INSERT INTO smoothies.public.orders (ingredients, name_on_order) VALUES (?, ?)"

    # Submit order button
    if st.button('Submit Order'):
        session.sql(my_insert_stmt, (ingredients_string, name_on_order)).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")

