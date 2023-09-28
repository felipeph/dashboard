# Biblioteca principal para geração da aplicação
import streamlit as st

import plotly.graph_objects as go


from pathlib import Path

import pandas as pd

# Utilizada para fazer o reload da página a cada 10 minutos
import time

# Conjunto de funções em código separado
import functions as f

# Configurações básicas da página
st.set_page_config(page_title="ACOPLAST Brasil",
                   page_icon="favicon-acoplast.ico",
                   layout="wide",
                   initial_sidebar_state="expanded",)

# CSS Hacks para remover cabeçalho padrão e posicionar as coisas direito
#f.remove_header()
#f.remove_top_padding()
f.remove_footer()
f.remove_toolbar()
f.change_header_background()
f.remove_top_padding()


# Coleta da chave API cadastrada no secrets do streamlit
chave_api = st.secrets["chave_api"]

# Criação do Dataframe com os dados coletados da lista de spots
spots_list_df = f.fetch_spots_list()

# Itens da barra lateral
with st.sidebar:
    
    # Logo da empresa
    st.image("logo_acoplast.png", use_column_width=True)
    
    st.header("ACODATA® CÓDIGO: 645205") # Colocar como parâmetro
    
    # Lista de itens para escolha
    st.session_state.spot_selected_name = st.radio(label="PONTOS DE MONITORAMENTO",
                                                   options=spots_list_df["spot_name"])
    
    st.write("Dados mais recentes:")
    
    # Filtra o data frame para apenas a linha que contém o mesmo nome escolhido pelo usuário
    spot_id_selected = spots_list_df.loc[spots_list_df["spot_name"] == st.session_state.spot_selected_name]
    
    # Dentro da do novo data frame, pega apenas o valor que está na coluna spot_id
    st.session_state.spot_id_selected = spot_id_selected["spot_id"].tolist()[0]
    
    
# st.title("ACODATA®    ‎ ‎ ‎Sistema de Monitoramento de Ativos")

# st.header("Teste")

st.divider()

# Título da página
st.header(f"{st.session_state.spot_selected_name}")

# Coletas as variáveis disponíves em um dado spot
spot_variables_df_api = f.fetch_variables_from_spot(st.session_state.spot_id_selected)

# Limpa as variáveis para apenas as que não são RMS 
spot_variables_df_api = spot_variables_df_api.dropna(subset=['alarm_critical'])

# Adicionar uma nova coluna com valores 0 para o dataframe
spot_variables_df_api["last_value"] = 0

csv_file_name = f"spot_{st.session_state.spot_id_selected}.csv"


csv_file_path = Path(csv_file_name)


if csv_file_path.is_file():
    pass
    #st.success(f"O arquivo {csv_file_name} existe.")
else:
    #st.error(f"O arquivo {csv_file_name} não existe.")
    spot_variables_df_api.to_csv(csv_file_name, index=False)

spot_variables_df_custom = pd.read_csv(csv_file_name)



# Loop para criação dos gráficos
for variable in spot_variables_df_custom["global_data_id"]:

    
    # Coleta dos dados de uma dada variável
    spot_variables_data_df = f.fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable)    
    
    
    # Coleta o nome da variável em questão
    variable_name = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["global_data_name"].tolist()[0]
    
    if variable_name == "VELOCIDADE":
        variable_name = "Velocidade - mm/s"
        df_header = ["Vertical", "Horizontal", "Axial", "timestamp"]
    if variable_name == "ACELERAÇÃO":
        variable_name = "Aceleração - g"
        df_header = ["Vertical", "Horizontal", "Axial", "timestamp"]
    if variable_name == "TEMPERATURA":
        variable_name = "Temperatura - °C"
        df_header = ["Temperatura", "timestamp"]
        
    spot_variables_data_df.columns = df_header
    
    number_of_variables = len(df_header)
    
    alarm_alert = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_alert"].tolist()[0]

    alarm_critical = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["alarm_critical"].tolist()[0]


    last_row = spot_variables_data_df.iloc[-1]
    
    last_timestamp = last_row["timestamp"]
    
    last_row = last_row[:-1]
       
    last_row_columns_names = last_row.index.tolist()
    
    last_row_values = last_row.values.tolist()

    values_to_evalute = last_row_values + [float(alarm_critical)]

    max_x_value = max(values_to_evalute)

    def assign_color(value):
        if value > alarm_critical:
            return "red"
        elif value < alarm_alert:
            return "green"
        else:
            return "gold"
        
    colors_list = last_row.apply(assign_color).tolist()
    

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
    
    fig.update_xaxes(range=[0, max_x_value*1.2])
    
    fig.add_vline(x=alarm_alert, line_dash="dash", line_color="gold")
    fig.add_vline(x=alarm_critical, line_dash="dash", line_color="red")

    fig.update_layout(height=number_of_variables*30)
    #fig.update_layout(title=variable_name)
    fig.update_layout(showlegend=False)
    config = {'staticPlot': True}
    
    
    
    fig.update_layout(margin=dict(t=0, b=0))

    st.sidebar.subheader(variable_name)
    st.sidebar.plotly_chart(fig, theme="streamlit", use_container_width=True, config = config)
    
    
    with st.container():
        column_plot, column_config = st.columns([0.8, 0.2], gap="small")
        with column_plot:
        
            f.plot_dataframe_lines(spot_variables_data_df, variable_name, alarm_alert, alarm_critical)
        
        with column_config:
            with st.expander("Configurações do gráfico:"):
                with st.form(key=variable_name):
                    alarm_alert_custom = st.number_input(label="Alarme de Alerta", 
                                                        value=alarm_alert,
                                                        key=variable_name+"alarm_alert")
                    alarm_critical_custom = st.number_input(label="Alarme Crítico", 
                                                            value=alarm_critical,
                                                            key=variable_name+"alarm_critical")
                    alarm_settings_changed = st.form_submit_button("Salvar")
                    if alarm_settings_changed:
                        spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_alert"] = alarm_alert_custom
                        spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_critical"] = alarm_critical_custom
                        spot_variables_df_custom.to_csv(csv_file_name, index=False)
                        st.experimental_rerun()

st.sidebar.caption(f"Atualizado em {last_timestamp}")               




# while True:
#     time.sleep(600)
#     st.experimental_rerun()


