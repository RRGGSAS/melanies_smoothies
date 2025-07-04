# Import python packages
import streamlit as st
import pandas as pd
import requests

#from snowflake.snowpark.context import get_active_session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(" 🥤 Customize Your Smoothie 🥤")
st.write(
  """Choose the fruits you want custom smoothie!
  """)

name_on_order = st.text_input("Name of Smoothie:")
st.write("The name of smoothie will be", name_on_order)

#para conectara a SniS (streamlit que no requiere cuenta pero debe ser público) 
#session = get_active_session()
cnx=st.connection("snowflake");
session=cnx.session();

my_dataframe = session.table("smoothies.public.fruit_options").select(col('FRUIT_NAME'),col('SEARCH_ON'))
#st.dataframe(data=my_dataframe, use_container_width=True)
#st.stop

# Convertir a pandas DataFrame
pd_df = my_dataframe.to_pandas()

# Mostrar en Streamlit
#st.dataframe(pd_df)

# Detener la ejecución (opcional)
#st.stop()

ingredients_list= st.multiselect(
'Choose up to 5 ingredients:', my_dataframe, max_selections=5
)
if ingredients_list:
    
    ingredients_string=''

    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen +' '

        search_on=pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
        #st.write('The search value for ', fruit_chosen,' is ', search_on, '.')

        st.subheader(fruit_chosen +' Nutrition Information') 
        smoothiefroot_response = requests.get("https://my.smoothiefroot.com/api/fruit/" + search_on)
        sf_df = st.dataframe(data=smoothiefroot_response.json(), use_container_width=True)

    st.write(ingredients_string)

    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,name_on_order)
                values ('""" + ingredients_string + """','""" + name_on_order + """')"""
    
    st.write(my_insert_stmt)
    #st.stop
    
    time_to_insert= st.button('Submit order')
    
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered'+','+ name_on_order +'!', icon="✅")
