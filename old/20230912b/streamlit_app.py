import streamlit as st

import time

from functions import fetch_spots_list, fetch_variables_from_spot, fetch_data_from_variable_from_spot, plot_dataframe_lines, remove_header, remove_top_padding

from streamlit_extras.app_logo import add_logo


st.set_page_config(page_title="Dashboard ACOPLAST Brasil",
                   page_icon="favicon-acoplast.ico",
                   layout="wide",
                   initial_sidebar_state="expanded",)

remove_header()

remove_top_padding()

chave_api = st.secrets["chave_api"]

spots_list_df = fetch_spots_list()

# Itens da barra lateral
with st.sidebar:
    
    # Logo da empresa
    st.image("logo_acoplast.png")
    
    # Lista de itens para escolha
    
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")
    st.write("Barra Lateral")



# Título da página
#st.image("logo_acoplast.png")
st.title("Dashboard ACOPLAST Brasil")
st.header("Consumo dos dados um por vez")

# Listagem de SPOTS pelo consumo da API
st.write(spots_list_df)

# Escolha o SPOT para análise
spot_selected = st.selectbox(label = "Escolha o sensor para análise",
                             options = spots_list_df["spot_id"])

# Coletas as variáveis disponíves em um dado spot
spot_variables_df = fetch_variables_from_spot(spot_selected)

# Exibe a lista das variáveis disponíveis
st.write(spot_variables_df)

# Caixa de seleção para qual a variável a ser analisada
variable_selected = st.selectbox(label="Escolha a variável para análise",
                                 options=spot_variables_df["global_data_id"])

# Coleta dos dados da variável solicitada nas últimas 24hrs
spot_variables_data_df = fetch_data_from_variable_from_spot(spot_selected, variable_selected)

# Desenha o gráfico de cada variável 
plot_dataframe_lines(spot_variables_data_df)


# while True:
#     time.sleep(600)
#     st.experimental_rerun()


