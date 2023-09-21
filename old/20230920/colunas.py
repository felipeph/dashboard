# Biblioteca principal para geração da aplicação
import streamlit as st

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
spot_variables_df = fetch_variables_from_spot(st.session_state.spot_id_selected)

# Limpa as variáveis para apenas as que não são RMS 
spot_variables_df = spot_variables_df.dropna(subset=['alarm_critical'])

columns_number = len(spot_variables_df)

columns_names = spot_variables_df["global_data_name"]

#st.write(columns_number)

#st.write(columns_names)

columns = st.columns(columns_number)

#st.write(columns_names)

for i, column in enumerate(columns):
    with column:
        variable_name = columns_names[i]
        #st.subheader(variable_name)
        variable_row = spot_variables_df[spot_variables_df["global_data_name"] == variable_name]
        #st.write(variable_row)
        variable_id = variable_row["global_data_id"].tolist()[0]
        #st.write(variable_id)
        spot_variables_data_df = fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable_id)
        #st.write(spot_variables_data_df)
        plot_dataframe_lines(spot_variables_data_df, variable_name, 25, 30)
        
        

# Loop para criação dos gráficos
# for variable in spot_variables_df["global_data_id"]:
    
#     # Coleta dos dados de uma dada variável
#     spot_variables_data_df = fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable)
    
#     # Coleta o nome da variável em questão
#     variable_name = spot_variables_df[spot_variables_df["global_data_id"] == variable]["global_data_name"].tolist()[0]

#     for column in columns_names:
#         with column:         

#             # Cria os gráficos um abaixo do outro    
#             plot_dataframe_lines(spot_variables_data_df, variable_name, 25, 30)
            



# while True:
#     time.sleep(600)
#     st.experimental_rerun()


