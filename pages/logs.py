import streamlit as st

st.set_page_config(page_title= "Logs de consulta da API",
                   page_icon="favicon-acoplast.ico",
                   layout="wide",
                   initial_sidebar_state="collapsed"
                   )

with open("api_requests.log", "r") as file:
    content = file.read()

num_lines = content.count('\n') + 1

# Exibindo o número de linhas no Streamlit
st.text(f"Número de linhas: {num_lines}")

# Exibindo o conteúdo no Streamlit
st.text(content)