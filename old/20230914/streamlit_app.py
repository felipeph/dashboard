# Biblioteca principal para geração da aplicação
import streamlit as st

from pathlib import Path

import pandas as pd

# Utilizada para fazer o reload da página a cada 10 minutos
import time

# Conjunto de funções em código separado
from functions import fetch_spots_list, fetch_variables_from_spot, fetch_data_from_variable_from_spot, plot_dataframe_lines, remove_header, remove_top_padding


# Configurações básicas da página
st.set_page_config(page_title="Dashboard ACOPLAST Brasil",
                   page_icon="favicon-acoplast.ico",
                   layout="wide",
                   initial_sidebar_state="expanded",)

# CSS Hacks para remover cabeçalho padrão e posicionar as coisas direito
remove_header()
remove_top_padding()

# Coleta da chave API cadastrada no secrets do streamlit
chave_api = st.secrets["chave_api"]

# Criação do Dataframe com os dados coletados da lista de spots
spots_list_df = fetch_spots_list()

# Itens da barra lateral
with st.sidebar:
    
    # Logo da empresa
    st.image("logo_acoplast.png")
    
    st.header("Plataforma de Testes")
    
    # Lista de itens para escolha
    st.session_state.spot_selected_name = st.radio(label="Sensores:",
                                                   options=spots_list_df["spot_name"])
    
    # Filtra o data frame para apenas a linha que contém o mesmo nome escolhido pelo usuário
    spot_id_selected = spots_list_df.loc[spots_list_df["spot_name"] == st.session_state.spot_selected_name]
    
    # Dentro da do novo data frame, pega apenas o valor que está na coluna spot_id
    st.session_state.spot_id_selected = spot_id_selected["spot_id"].tolist()[0]
    
    
# Título da página
st.header(f"Dashboard ACOPLAST Brasil: {st.session_state.spot_selected_name}")

# Coletas as variáveis disponíves em um dado spot
spot_variables_df_api = fetch_variables_from_spot(st.session_state.spot_id_selected)

# Limpa as variáveis para apenas as que não são RMS 
spot_variables_df_api = spot_variables_df_api.dropna(subset=['alarm_critical'])

csv_file_name = f"spot_{st.session_state.spot_id_selected}.csv"

#st.write(csv_file_name)

csv_file_path = Path(csv_file_name)

#st.write(csv_file_path)

if csv_file_path.is_file():
    pass
    #st.success(f"O arquivo {csv_file_name} existe.")
else:
    #st.error(f"O arquivo {csv_file_name} não existe.")
    spot_variables_df_api.to_csv(csv_file_name, index=False)

spot_variables_df_custom = pd.read_csv(csv_file_name)

#st.write(spot_variables_df_custom)

# Loop para criação dos gráficos
for variable in spot_variables_df_custom["global_data_id"]:

    
    # Coleta dos dados de uma dada variável
    spot_variables_data_df = fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable)
    
    # Coleta o nome da variável em questão
    variable_name = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["global_data_name"].tolist()[0]

    alarm_alert = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_alert"].tolist()[0]
    
    #st.write(alarm_alert)

    alarm_critical = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_critical"].tolist()[0]
    
    #st.write(alarm_critical)

    # Cria os gráficos um abaixo do outro    
    plot_dataframe_lines(spot_variables_data_df, variable_name, alarm_alert, alarm_critical)
    
    with st.expander("Configurações do gráfico:"):
        with st.form(key=variable_name):
            col1, col2 = st.columns(2)
            with col1:    
                alarm_alert_custom = st.number_input(label="Alarme de Alerta", 
                                                    value=alarm_alert,
                                                    key=variable_name+"alarm_alert")
            with col2:
                alarm_critical_custom = st.number_input(label="Alarme Crítico", 
                                                        value=alarm_critical,
                                                        key=variable_name+"alarm_critical")
            alarm_settings_changed = st.form_submit_button("Salvar")
            if alarm_settings_changed:
                spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_alert"] = alarm_alert_custom
                spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_critical"] = alarm_critical_custom
                #st.write(spot_variables_df_custom)
                spot_variables_df_custom.to_csv(csv_file_name, index=False)
                #st.success("Dados alterados com sucesso")
                st.experimental_rerun()
                




# while True:
#     time.sleep(600)
#     st.experimental_rerun()


