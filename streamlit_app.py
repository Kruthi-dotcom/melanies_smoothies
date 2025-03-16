# Import required packages
import requests
import streamlit as st
from snowflake.snowpark.functions import col

# Streamlit UI
st.title("🥤 Customize Your Smoothie! 🥤")
st.write("Choose the fruits you want in your custom Smoothie!")

# Input for name on the smoothie
name_on_order = st.text_input('Name on Smoothie:')
st.write('The name on your Smoothie will be:', name_on_order)

# Connect to Snowflake
cnx = st.connection("snowflake")
session = cnx.session()

# Fetch fruit options from Snowflake
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON'))

# Convert the Snowpark DataFrame to a Pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Debugging step: Check if data is fetched correctly
st.write("Fetched Fruits Data:")
st.dataframe(pd_df)

# Ensure pd_df is not empty
if pd_df.empty:
    st.error("No fruit options available! Please check the database.")
    st.stop()

# Create multiselect dropdown for ingredients
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    pd_df['FRUIT_NAME'].tolist(),  # Convert column to list
    max_selections=5
)

# Stop execution for debugging (after multiselect so it functions correctly)
st.stop()

if ingredients_list:
    ingredients_string = ''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '

        # Get the corresponding SEARCH_ON value
        search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]

        # Display nutrition info
        st.subheader(f'{fruit_chosen} Nutrition Information')
        fruityvice_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_on}")

        if fruityvice_response.status_code == 200:
            st.dataframe(fruityvice_response.json(), use_container_width=True)
        else:
            st.write(f"Could not fetch data for {fruit_chosen}")

    # Insert order into the database
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, name_on_order)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    # Order button
    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")
