# Fetch fruit options with both display name and search term
my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'), col('SEARCH_ON')).collect()

# Convert to dictionary for easy lookup
fruit_dict = {row["FRUIT_NAME"]: row["SEARCH_ON"] for row in my_dataframe}

# Multiselect with display names
ingredients_list = st.multiselect(
    'Choose up to 5 ingredients:',
    list(fruit_dict.keys()),  # Show user-friendly names
    max_selections=5
)

if ingredients_list:
    ingredients_string = ''
    
    for fruit_chosen in ingredients_list:
        search_term = fruit_dict[fruit_chosen]  # Get correct search term
        ingredients_string += fruit_chosen + ' '  # Store as user-friendly name

        smoothiefroot_response = requests.get(f"https://my.smoothiefroot.com/api/fruit/{search_term}")
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    my_insert_stmt = f"""
        INSERT INTO smoothies.public.orders (ingredients, name_on_order)
        VALUES ('{ingredients_string}', '{name_on_order}')
    """

    time_to_insert = st.button('Submit Order')

    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success(f'Your Smoothie is ordered! {name_on_order}', icon="✅")


