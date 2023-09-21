# Biblioteca principal para geração da aplicação
import streamlit as st

import plotly.graph_objects as go


from pathlib import Path

import pandas as pd

# Utilizada para fazer o reload da página a cada 10 minutos
import time

# Conjunto de funções em código separado
from functions import fetch_spots_list, fetch_variables_from_spot, fetch_data_from_variable_from_spot, plot_dataframe_lines, remove_header, remove_top_padding


# Configurações básicas da página
st.set_page_config(page_title="ACOPLAST Brasil",
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
    st.image("logo_acoplast.png", use_column_width=True)
    
    st.header("Plataforma de Testes")
    
    # Lista de itens para escolha
    st.session_state.spot_selected_name = st.radio(label="Sensores:",
                                                   options=spots_list_df["spot_name"])
    
    st.write("Dados mais recentes:")
    
    # Filtra o data frame para apenas a linha que contém o mesmo nome escolhido pelo usuário
    spot_id_selected = spots_list_df.loc[spots_list_df["spot_name"] == st.session_state.spot_selected_name]
    
    # Dentro da do novo data frame, pega apenas o valor que está na coluna spot_id
    st.session_state.spot_id_selected = spot_id_selected["spot_id"].tolist()[0]
    
    
st.title("ACODATA®    ‎ ‎ ‎Sistema de Monitoramento de Ativos")

# Título da página
st.header(f"{st.session_state.spot_selected_name}")

# Coletas as variáveis disponíves em um dado spot
spot_variables_df_api = fetch_variables_from_spot(st.session_state.spot_id_selected)

# Limpa as variáveis para apenas as que não são RMS 
spot_variables_df_api = spot_variables_df_api.dropna(subset=['alarm_critical'])

# Adicionar uma nova coluna com valores 0 para o dataframe
spot_variables_df_api["last_value"] = 0

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
    
    #st.write(spot_variables_data_df)
    

    
    
    #st.sidebar.dataframe(last_row)
    
    # Coleta o nome da variável em questão
    variable_name = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["global_data_name"].tolist()[0]

    alarm_alert = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_alert"].tolist()[0]
    
    #st.write(alarm_alert)

    alarm_critical = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_critical"].tolist()[0]
    
    
    # fig = go.Figure(go.Indicator(
    #     mode = "gauge+number",
    #     value = 270,
    #     domain = {'x': [0, 1], 'y': [0, 1]},
    #     title = {'text': "Speed"}))
    
    #fig.update_layout(height=200)


    last_row = spot_variables_data_df.iloc[-1]
    
    last_timestamp = last_row["timestamp"]
    
    last_row = last_row[:-1]
    
    #st.sidebar.write(last_row)
    
    #last_row["alarm_alert"] = alarm_alert
    
    #last_row["alarm_critical"] = alarm_critical
    
    #st.sidebar.write(last_row)
    
    last_row_columns_names = last_row.index.tolist()
    
    last_row_values = last_row.values.tolist()
    
    #st.sidebar.write(last_row_columns_names)

    def assign_color(value):
        if value > alarm_critical:
            return "red"
        elif value < alarm_alert:
            return "green"
        else:
            return "gold"
        
    colors_list = last_row.apply(assign_color).tolist()
    
    #st.write(colors_list)
    

    fig = go.Figure(go.Bar(
        x=last_row_values,
        y=last_row_columns_names,
        orientation='h',
        marker_color=colors_list,
        text=last_row_values,  # Use os valores como texto
        textposition='outside',
        insidetextanchor='end',
        textangle=0,
        texttemplate='%{text:.3f}',# Posicione o texto dentro das barras
    ))    
    
    fig.add_vline(x=alarm_alert, line_dash="dash", line_color="gold")
    fig.add_vline(x=alarm_critical, line_dash="dash", line_color="red")

    fig.update_layout(height=100)
    fig.update_layout(showlegend=False)
    config = {'staticPlot': True}
    
    fig.update_layout(margin=dict(t=0, b=0))


    st.sidebar.plotly_chart(fig, theme="streamlit", use_container_width=True, config = config)
    
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

st.sidebar.caption(f"Atualizado em {last_timestamp}")               




while True:
    time.sleep(600)
    st.experimental_rerun()


