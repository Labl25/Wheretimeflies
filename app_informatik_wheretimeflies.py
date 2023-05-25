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

tab1, tab2, tab3, tab4 = st.tabs(["Where time flies", "Input descriptions", "Activity input", "Daily notes"])

with tab1:    
    st.title('Where time flies')
    st.markdown("_An App designed for you to become more aware of your own daily activities_")
#Inputs explanation
with tab2:
    st.markdown('**Input description**')
    st.markdown('_Sleep hours_: Time spent actually sleeping.')
    st.markdown('_Time spent eating_: Time spent actually eating regardless of this beeing done while sitting or standing.')
    st.markdown('_Time spent sitting_: Time spent sitting, regardless of it being done while working or doing a hobby.')
    st.markdown('_Time spent walking_: Time spent only walking (from and to work, with your dog or just because).')
    st.markdown('_Time spent working out_: Time spent running, playing a sport or doing a workout (warm ups must be included).')
    st.markdown('_Time spent on hobby_: Time spent doing a non high active free-time activity like cooking, reading, scrolling through social media and such.')
    st.markdown('Every category can be left blank. However, the total of entered hours cannot exceed 24h.')
    st.markdown('_Remaining time_ is here a as guide to not threspass the 24h per day limit (_entered hours_ <= 24h).')

with tab3:
    st.subheader('Input categories')
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
    
# Arrange 3 buttons into 3 columns
    Col0, Col1, Col2= st.columns(3) 
# Show and submit button defined as run and show all data as run1 as well as delete      
    run_today = Col0.button("Submit today's data") 
    run_saved = Col1.button('Show all data', key = 'all_data')
    delete = Col2.button('Delete last input', key = 'last_input' )

    if run_today:
    #Subheader of dataframe table
        st.subheader("Today's overview")
    # Only user inputs with a total of max 24h will be added to the dataframe, otherwise warning will pop up.  
        if total_hours <= 24:
        
            new_data = {'Day and month': date, 
                   'Sleep hours': sleep,
                   'Time spent eating': food,
                   'Time spent sitting': sitting,
                   'Time spent walking': walking,
                   'Time spent working out': workout,
                   'Time spent on hobby': hobby} 
        #load data to jsonbin             
            accu_data = load_key(api_key, bin_id, username)
            accu_data.append(new_data)
            res = save_key(api_key, bin_id, username, accu_data)
            if 'message' in res:
                st.error(res['message'])
        #new_data to df dataframe
            df = pd.DataFrame(new_data, index = [date])
            st.dataframe(df)
        # Descriptive title and text for chart from user input dataframe
            st.subheader("Today's pie chart")
            st.text("Today's activity overview in percentages")
        
        # Create a piechart with df as dataframe
            aggregated_data = df.drop('Day and month', axis=1).sum()
            fig = px.pie(aggregated_data, values=aggregated_data.values, names=aggregated_data.index)
            st.plotly_chart(fig)        
        else:
            st.warning("A day does not have more than 24 hours!") 
        
#See all saved data (all inputs) as df1 
    if run_saved:
    #Subheader of dataframe table
        st.subheader('Daily overview')
        accu_data = load_key(api_key, bin_id, username)
        df1 = pd.DataFrame(accu_data)
    #Warning if there is no data saved from previous days
        if len(df1) == 0:
            st.warning('No data available')    
        else: 
        # Depict all saved data as df1 dataframe
            st.dataframe(df1) 
        #Descriptive title and text for chart from user input dataframe
            st.subheader('Graphical summary')
            st.markdown('Graphical overview of daily activity by date _(in hours)_')
    #Create a barchart with older saved data (df4)
            chart_data = pd.DataFrame(df1)
            st.bar_chart(data= chart_data, x ='Day and month', 
                    y = ['Sleep hours',
                     'Time spent eating',
                     'Time spent sitting',
                     'Time spent walking',
                     'Time spent working out',
                     'Time spent on hobby']
                 )
        
#Delete last input    
    if delete:
        accu_data = load_key(api_key, bin_id, username)
        accu_data.pop()
        res = save_key(api_key, bin_id, username, accu_data)
    
        if 'message' in res:
            st.error(res['message'])
    

with tab4:
    Col0, Col2 = st.columns(2)
    Col0 = Col0.date_input(label = "Date")
    Col2 = Col2.text_area(label = "Today's notes")
    
    Submit = st.button("Submit", key = "sub_notes")
    Show_older_notes = st.button(" Show older notes", key = "show_older")
                                 
    if Submit:
        new_notes = {'Date': Col0, 
                   "Today's notes": Col2,
                   } 
        #load data to jsonbin             
        accu_notes = load_key(api_key, bin_id, username)
        accu_notes.append(new_notes)
        res = save_key(api_key, bin_id, username, accu_notes)
        if 'message' in res:
            st.error(res['message'])
        #new_data to df dataframe
    if Show_older_notes:
        df2 = pd.DataFrame(new_notes, index = [date])
        st.dataframe(df2)















    

    
    
