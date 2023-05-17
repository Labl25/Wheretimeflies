# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 18:32:14 2023

@author: Startklar
"""

import streamlit as st
import pandas as pd
import plotly.express as px

from geocode import get_coordinates
from jsonbin import load_key, save_key
import yaml
from yaml.loader import SafeLoader
import streamlit_authenticator as stauth


DATA_FILE = "saved_data.json"
st.set_page_config(
                    page_title="App_Informatik",
                    page_icon="running",
                    layout="wide",
                    initial_sidebar_state="expanded"
                    )

# -------- load secrets for jsonbin.io --------
jsonbin_secrets = st.secrets["jsonbin"]
api_key = jsonbin_secrets["api_key"]
bin_id = jsonbin_secrets["bin_id"]

# -------- user login --------
with open('config.yaml') as file:
    config = yaml.load(file, Loader=SafeLoader)

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
)

fullname, authentication_status, username = authenticator.login('Login', 'main')

if authentication_status == True:   # login successful
    authenticator.logout('Logout', 'main')   # show logout button
elif authentication_status == False:
    st.error('Username/password is incorrect')
    st.stop()
elif authentication_status == None:
    st.warning('Please enter your username and password')
    st.stop()


# Arrange 2 buttons into 2 columns
Col0, Col1= st.columns(2) 
# Show and submit button defined as run and show all data as run1      
run_today = Col0.button("Show and submit today's data") 
run_saved = Col1.button('Show all data', key = 'all_data')

#Subheader of dataframe table
st.subheader('Input data table')

# Dataframe
df = pd.DataFrame({'Day and month': date, 
                   'Sleep hours': sleep,
                   'Time spent eating': food,
                   'Time spent sitting': sitting,
                   'Time spent walking': walking,
                   'Time spent working out': workout,
                   'Time spent on hobby': hobby}, 
                   index = [date]
                   )             

# Df2 as table from df1, which adds every new user input to the datatable
df1 = pd.concat([st.session_state.mdf, df], ignore_index= False) 

# Stop date duplications. Only the last date input will be shown in dataframe
df2 = df1.drop_duplicates(subset=['Day and month'], keep='last')  
 
# Redefine df1 and df2 ad df3    
df3 = pd.DataFrame(df2) 
# read in existing and saved data
df4 = pd.read_json(DATA_FILE)

if run_today:
    # Only user inputs with a total of max 24h will be added to the dataframe, otherwise warning will pop up.  
    if total_hours <= 24:
        # Check if df4 is empty or not
        if df4.empty:
            # If it's empty, assign the new input data to it
            df4 = df3.copy()
        else:
            # If it's not empty, append the new input data to it while dropping duplicates
            df4 = pd.concat([df4, df3], ignore_index=True)
            df4 = df4.drop_duplicates(subset= ['Day and month'], keep='last')
        
        # Save dataframe as json
        df4.to_json(DATA_FILE, orient='records')
        
        # Show dataframe df = User input
        st.dataframe(df)
        
        # Descriptive title and text for chart from user input dataframe
        st.subheader('Pie chart of today')
        st.text('Percentage of time spent in each category today')
        
        # Create a piechart with df as dataframe
        aggregated_data = df.drop('Day and month', axis=1).sum()
        fig = px.pie(aggregated_data, values=aggregated_data.values, names=aggregated_data.index)
        st.plotly_chart(fig)
        
    else:
        st.warning("A day does not have more than 24 hours!") 
 
if run_saved:
    # Show df4 dataframe
    st.dataframe(df4)
    
    # Descriptive title and text for chart from user input dataframe
    st.subheader('Yearly graphical display')
    st.text('Time spent for each category with latest input')
    
    # Create a barchart with older saved data (df4)
    chart_data = pd.DataFrame(df4)
    st.bar_chart(data= chart_data, x ='Day and month', 
                 y = ['Sleep hours',
                     'Time spent eating',
                     'Time spent sitting',
                     'Time spent walking',
                     'Time spent working out',
                     'Time spent on hobby']
                 )


 
    

















    

    
    
