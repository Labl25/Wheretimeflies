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

def Zählung_Dictionary():
    #Regeneriert die Zählung in session_state zu Dictionary
    Dictionary = {}
    zaehler = ['Day and month', 'Sleep hours', 'Time spent eating', 'Time spent sitting', 'Time spent walking', 'Time spent working out','Time spent on hobby']                                      
    for key in zaehler:
        Dictionary[key]=st.session_state[key]
    return Dictionary


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

st.title('Where time flies')

#Inputs explanation
st.subheader('Input categories')
st.markdown('**Input explanation**')
st.markdown('_Sleep hours_: Time spent actually sleeping.')
st.markdown('_Time spent eating_: Time spent actually eating regardless of this beeing done while sitting or standing.')
st.markdown('_Time spent sitting_: Time spent sitting, regardless of it being done while working or doing a hobby.')
st.markdown('_Time spent walking_: Time spent only walking (from and to work, with your dog or just because).')
st.markdown('_Time spent working out_: Time spent running, playing a sport or doing a workout (warm ups must be included).')
st.markdown('_Time spent on hobby_: Time spent doing a non high active free-time activity like cooking, reading, scrolling through social media and such.')
st.markdown('Every category can be left blank. However, the total of entered hours cannot exceed 24h.')
st.markdown('_Remaining time_ is here a as guide to not threspass the 24h per day limit (_entered hours_ <= 24h).')



# Create input columns
Col0, Col1, Col2, Col3, Col4, Col5, Col6, Col7 = st.columns(8) 
date = Col0.date_input(label = "Day and month").strftime("%Y-%m-%d")
sleep = Col1.number_input(label="Sleep hours", min_value = 0.0, max_value=24.0) 
food = Col2.number_input(label="Time spent eating", min_value = 0.0, max_value=24.0)
sitting = Col3.number_input(label="Time spent sitting", min_value = 0.0, max_value=24.0) 
walking = Col4.number_input(label="Time spent walking", min_value = 0.0, max_value=24.0) 
workout = Col5.number_input(label="Time spent working out", min_value = 0.0, max_value=24.0)
hobby = Col6.number_input(label="Time spent on hobby", min_value = 0.0, max_value=24.0)
   
# Calculate total_hours and not_accounted_for
total_hours = sleep + food + sitting + walking + workout + hobby
not_accounted_for = 24 - (total_hours) 
# Define active as the sum of walking and workout hours
active = walking + workout 

# Create Col7 with not_accounted_for
with Col7:
    st.text('Remaining time') 
    Col7.write(not_accounted_for)
    
# Being active recomendation, which if bieing less than 21 min, a warning will be present.
if active < 0.35: 
    st.warning("WHO recomends an adult person to be active for at least for 21 min per day") 
    
# Arrange 2 buttons into 2 columns
Col0, Col1= st.columns(2) 
# Show and submit button defined as run and show all data as run1      
run_today = Col0.button("Show and submit today's data") 
run_saved = Col1.button('Show all data', key = 'all_data')

#Subheader of dataframe table
st.subheader('Input data table')

# Dataframe
#df = pd.DataFrame({'Day and month': date, 
                   #'Sleep hours': sleep,
                   #'Time spent eating': food,
                   #'Time spent sitting': sitting,
                   #'Time spent walking': walking,
                   #'Time spent working out': workout,
                   #'Time spent on hobby': hobby}, 
                   #index = [date]
                   #)             

# Df2 as table from df1, which adds every new user input to the datatable
#df1 = pd.concat([st.session_state.mdf, df], ignore_index= False) 

# Stop date duplications. Only the last date input will be shown in dataframe
#df1 = df.drop_duplicates(subset=['Day and month'], keep='last')  
 
# Redefine df1 and df2 ad df3    
#df2 = pd.DataFrame(df1) 
# read in existing and saved data
#df3 = pd.read_json(DATA_FILE)
#df4 = load_data(api_key, bin_id)
#df4 = load_key(api_key, bin_id, username)

#st.write(df4)
if run_today:
    # Only user inputs with a total of max 24h will be added to the dataframe, otherwise warning will pop up.  
    if total_hours <= 24:
        
        new_data = {'Day and month': date, 
                   'Sleep hours': sleep,
                   'Time spent eating': food,
                   'Time spent sitting': sitting,
                   'Time spent walking': walking,
                   'Time spent working out': workout,
                   'Time spent on hobby': hobby} 
                     
        accu_data = load_key(api_key, bin_id, username)
        accu_data.append(new_data)
        #accu_data = df1.drop_duplicates(subset= ['Day and month'], keep='last')
        res = save_key(api_key, bin_id, username, accu_data)
        
        df = pd.DataFrame(new_data, index = [date])
        st.table(df)
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
    delete = st.button("delete") 
    if delete:
        accu_data = load_key(api_key, bin_id, username)
        accu_data.pop()
        res = save_key(api_key, bin_id, username, accu_data)
    # Show df1 dataframe
    df1 = pd.DataFrame(accu_data)
    st.table(df1)
    
    # Descriptive title and text for chart from user input dataframe
    st.subheader('Yearly graphical display')
    st.text('Time spent for each category with latest input')
    
    # Create a barchart with older saved data (df4)
    chart_data = pd.DataFrame(df1)
    st.bar_chart(data= chart_data, x ='Day and month', 
                 y = ['Sleep hours',
                     'Time spent eating',
                     'Time spent sitting',
                     'Time spent walking',
                     'Time spent working out',
                     'Time spent on hobby']
                 )

 
    

















    

    
    
