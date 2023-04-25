# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 18:32:14 2023

@author: Startklar
"""

import streamlit as st
import pandas as pd
import numpy as np
from PIL import Image
import time 
import plotly.express as px
import altair as alt
import json

st.set_page_config(
    page_title="App_Informatik",
    page_icon="moon",
    layout="wide",
    initial_sidebar_state="expanded"
    )

DATA_FILE = "app_info.json"

# Funktion zum Laden der Adressliste aus einer JSON-Datei
def load_data():
    with open(DATA_FILE, "r") as file:
        data = json.load(file)
    return data

# Funktion zum Speichern der Adressliste in einer JSON-Datei
def save_data(data):
    with open(DATA_FILE, "w") as file:
        json.dump(data,file,indent=8,ensure_ascii=False)

# Laden der vorhandenen input daten
input_hours = load_data()


st.title('Where time flies')

# inputs in columns
st.subheader('Input cathegories')
st.markdown('**Input explanation**')
st.markdown('_Sleep hours_: Time spent actually sleeping.')
st.markdown('_Time spent eating_: Time spent actually eating regardless of this beeing done while sitting or standing.')
st.markdown('_Time spent sitting_: Time spent sitting, regardless of it being done while working, doing a hobby or working.')
st.markdown('_Time spent walking_: Time spent only walking (from and to work, with your dog or just because.')
st.markdown('_Time spent working out_: Time spent running, playing a sport or doing a workout (warm ups must be included).')
st.markdown('_Time spent on hobby_: Time spent doing a non high active free-time activity like cooking, reading, scrolling through social media and such.')
st.markdown('Every cathegory can be left blank. However, the total of enterded hours cannot exceed 24h.')
st.markdown('_Not accounted for_ is here a as guide to not threspass the 24h per day limit (_entered hours_ <= 24h).')

if "mdf" not in st.session_state:
    st.session_state.mdf = pd.DataFrame(columns=['Day and month', 'Sleep hours', 'Time spent eating', 
                                                 'Time spent sitting', 'Time spent walking', 
                                                 'Time spent working out','Time spent on hobby'])
Col0, Col1, Col2, Col3, Col4, Col5, Col6, Col7 = st.columns(8)  
date = Col0.date_input(label = "Day and month").strftime("%Y-%m-%d")
sleep = Col1.number_input(label="Sleep hours") 
food = Col2.number_input(label="Time spent eating")
sitting = Col3.number_input(label="Time spent sitting") 
walking = Col4.number_input(label="Time spent walking") 
workout = Col5.number_input(label="Time spent working out")
hobby = Col6.number_input(label="Time spent on hobby")

total_hours = sleep + food + sitting + walking + workout + hobby
not_accounted_for = 24 - (total_hours) 


# Create Col7 with not_accounted_for
with Col7:
    st.text('Remaining time') 
    Col7.write(not_accounted_for)
     

# Show and submit button defined as run and show all data as run1      
run_today = st.button("Show and submit today's data") 

st.subheader('Input data table')
 
# Being active recomendation, which if bieing less than 21 min, a warning will be present.                                 
active = walking + workout  
if active < 0.35:
    st.warning("WHO recomends an adult person to be active for at least for 21 min per day")    


if run_today:
    if total_hours <= 24:
        # Funktion zum Hinzufügen einer neuen Adresse zur Adressliste
        new_input = {'Day and month': date, 'Sleep hours': sleep, 'Time spent eating': food, 'Time spent sitting': sitting, 'Time spent walking': walking, 'Time spent working out': workout, 'Time spent on hobby': hobby} 
        input_hours.append(new_input) 
        save_data(input_hours)
        st.dataframe(new_input)
        
        # Descriptive title and text for chart from user input dataframe
        st.subheader('Pie chart of today')
        st.text('Percentage of time spent in each category today')
        
        # Create a piechart with df as dataframe -> no dataframe possible with JSON -> No Piechart.
        aggregated_data = new_input.drop('Day and month', axis=1).sum()
        fig = px.pie(aggregated_data, values=aggregated_data.values, names=aggregated_data.index)
        st.plotly_chart(fig)
            
    else:
        st.warning("A day does not have more than 24 hours!") 


# Darstellung der Adressliste als Tabelle
df0 = pd.DataFrame(input_hours)
st.table(df0)
# Convert the address list to a JSON string
json_string = df0.to_json(indent=8)

# Print the JSON string
print(json_string)   


 

                 














    

    
    