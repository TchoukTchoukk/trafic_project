import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import requests
from urllib.parse import quote



data = pd.read_csv("vitesse2021_reduit.csv")

df = data[:200000]

normalized = (df["speeddiff"] - df["speeddiff"].min()) / (df["speeddiff"].max() - df["speeddiff"].min())

colors = [(0, 0, 0.5) if value >= 0.5 else (float((1 - value)), 0, float(value)) for value in normalized]

df["color"] = colors



st.title('Trafic routier français en 2021')


page = st.sidebar.selectbox('Selectionner une page', ['Carte', 'Statistique'])


if page == 'Carte':
    st.sidebar.subheader('Filtrer les données')


    coordinate = [df['hour'].min()]

    search = st.text_input("Rechercher une ville/adresse :", "")

    encoded_string = quote(search)

    url = "https://api-adresse.data.gouv.fr/search/?q="+encoded_string+"&limit=1"
    response = requests.get(url).json()
    if search:
        st.write("Résultat de recherche pour : "+response["features"][0]["properties"]["label"]+"")
        coordinate = response["features"][0]["geometry"]["coordinates"]


    today = datetime.now() 
    hour = today.hour
    weekday = today.weekday()


    jours_semaine = ["Lundi", "Mardi", "Mercredi", "Jeudi", "Vendredi", "Samedi", "Dimanche"]
    selected_weekday = st.sidebar.select_slider('Plage de jours',value=(jours_semaine[weekday] ,jours_semaine[weekday]) ,options=jours_semaine) 

    selected_hour = st.sidebar.slider('Plage horaire', df['hour'].min(), df['hour'].max(),(hour,hour+2),format="%dh")

    month=["Janvier","Février","Mars","Avril","Mai","Juin","Juillet","Août", "Septembre", "Octobre", "Novembre", "Décembre"]
    selected_month = st.sidebar.select_slider('Plage de mois ', value =(month[df['month'].min()-1], month[df['month'].max()-1]),options=month)

    speed = ["50","70","80","90","110","130"]
    selected_speed = st.sidebar.select_slider('Plage de vitesse',options=speed,value=("50","130"))



    filtered = df[(df['weekday'] >= int(jours_semaine.index(selected_weekday[0]))) & (df['weekday'] <= int(jours_semaine.index(selected_weekday[1]))) & (df['hour'] >= selected_hour[0]) & (df['hour'] <= selected_hour[1])& (df['month'] >= int(month.index(selected_month[0]))) & (df['month'] <= int(month.index(selected_month[1]))) &(df['limite'] >= int(selected_speed[0])) & (df['limite'] <= int(selected_speed[1]))]
    
    if search:
        filtered = filtered[(filtered['lat'] >= coordinate[1]-0.4) & (filtered['lat'] <= coordinate[1]+0.4) &(filtered['lon'] >= coordinate[0]-0.3) & (filtered['lon'] <= coordinate[0]+0.3)]
    filtered= filtered.reset_index()


    st.subheader('_Carte interactive_',divider="blue")
    st.map(filtered,color="color")

   
    


if page == 'Statistique':
    st.subheader('_Statistique_',divider="blue")
    trafic = df[df["speeddiff"]<-10]
    
    weekday_counts = trafic["weekday"].value_counts().sort_index()
    hour_counts = trafic["hour"].value_counts()
    limite_counts = (trafic[(trafic['limite']>50)&(trafic['limite']<130)].groupby("limite").count()["speeddiff"]/df[(df['limite']>50)&(df['limite']<130)].groupby("limite").count()["speeddiff"])*100

    
    st.subheader("Nombre d'embouteillages par heure de la journée")
    st.bar_chart(hour_counts )
    st.subheader('',divider="blue")

    col, col2 = st.columns(2)
    with col:
        st.subheader("Nombre d'embouteillages par jour de la semaine")
        st.bar_chart(weekday_counts)

    with col2:
        st.subheader("%% d'embouteillement par vitesse limite")
        st.bar_chart(limite_counts)

    trafic = df[df["speeddiff"] < -10]
    weekday_counts = trafic["weekday"].value_counts()














