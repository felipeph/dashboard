import streamlit as st

import time

import pandas as pd

from functions import fetch_spots_list, fetch_variables_from_spot, fetch_data_from_variable_from_spot, plot_dataframe_lines

#chave_api = st.secrets["chave_api"]





# Título da página
st.title("Dashboard API Acoplast Brasil")
st.header("Consumo de todos os dados de uma vez só")

spots_list_df = fetch_spots_list()

# Listagem de SPOTS pelo consumo da API
st.write(spots_list_df)


# Get the list of sensors id
sensor_id_list = spots_list_df["sensor_id"].tolist()

# Create tabs for each sensor id
sensor_id_tabs = st.tabs(sensor_id_list)

# Iterate over the list of sensors and its tabs to populate them
for sensor_id, tab in zip(sensor_id_list, sensor_id_tabs):
    
    # Goes for each tab
    with tab:
        
        # Writes the name of the sensor for tests
        st.write(sensor_id)
        
        # Filter the df to the sensor id
        sensor_row = spots_list_df.loc[spots_list_df["sensor_id"] == sensor_id]
        
        st.write(sensor_row)
        
        # spot_selected = sensor_row["spot_id"]
        
        # spot_selected = spot_selected.iat[0,0]
        
        # st.write(spot_selected)
        
        # sensor_df = pd.DataFrame(sensor_row)
        
        # st.write(sensor_df)
        
        
        
        
        


# tabs_names = spots_list_df["sensor_id"].tolist()
# tabs_construct = st.tabs(tabs_names)
# for sensor, tabs_construct in zip(tab_names, tabs_construct):
#     st.write(sensor)
#     st.write(tabs_construct)
    

# st.write(tabs_names)

# tabs = st.tabs(tabs_names)

# st.write(tabs)

# #for tab_content in tabs_names:
    

# for index, row in spots_list_df.iterrows():
#     st.write(index)
#     st.write(row)
    
    

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


while True:
    time.sleep(600)
    st.experimental_rerun()


