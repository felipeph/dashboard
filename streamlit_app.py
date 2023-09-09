import streamlit as st
import parameters as p

chave_api = st.secrets["chave_api"]

st.title(p.titulo_pagina_inicial)
st.write(chave_api)

