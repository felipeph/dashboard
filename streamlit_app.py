# Streamlit to create the page
import streamlit as st

# My functions 
import functions as f

# Plotly to change elements in the plot
import plotly.graph_objects as go

# Pathlib to locate the CSV files
from pathlib import Path

# Pandas to manipulate the data
import pandas as pd

# Time to reload the app every 10 min
import time

from datetime import datetime

# My functions for style
import func_style as fs

# My functions for data
import func_data as fd

import func_params as fp

params_json_filepath = "params.json"

p = fp.load_params(params_json_filepath)

my_logo = "logo_acoplast.png"

client_logo = "logo_cliente.png"

spot_image = "pontos_monitoramento.png"

spots_list_csv = "spots_list.csv"

days_ago_7 = fd.n_days_ago(7)
today = fd.today()
fetch_data_from_date_interval = False


#........................ PAGE CONFIGURATION ............................................
# Adjust page configuration and hiding elements

st.set_page_config(page_title= p["page_config"]["page_title"],
                   page_icon="favicon-acoplast.ico",
                   layout="wide",
                   )

# Removing the header and the footer
fs.remove_streamlit_elements()
#---------------------------------------------------------------------------------------






#......................... FIRST API CALL ..............................................
# Coleta da chave API cadastrada no secrets do streamlit
api_key = st.secrets["chave_api"]

config_password = st.secrets["senha_config"]

# Criação do Dataframe com os dados coletados da lista de spots
spots_list_df = f.fetch_spots_list(api_key)

spots_list_df = fd.csv_for_spot_list(spots_list_df, spots_list_csv)
#---------------------------------------------------------------------------------------









#......................... HEADER ......................................................
# Sticky header with the logo and title of the page
header = st.container()

with header:
    header_left_col, header_center_col, header_right_col = header.columns([3,5,2], gap="small")
    header_left_col.image(my_logo, use_column_width=True)
    #header_center_col.markdown("""<div align="left"><h1 style="color:#2A4B80; display: inline">ACODATA®</h1><h6 style="color:#2A4B80; display: inline">CÓDIGO: 645205</h6></div>""", unsafe_allow_html=True)
    #header_right_col.image(client_logo, use_column_width="auto")
    header.write("""<div class='fixed-header'/>""", unsafe_allow_html=True)
    ### Custom CSS for the sticky header
    fs.sticky_header()
#---------------------------------------------------------------------------------------








#...................... COLUMNS OF THE BODY ............................................
# The body of the page with three columns
body = st.container()
with body:
    body_left_col, body_center_col = body.columns([3,7], gap="small")
#---------------------------------------------------------------------------------------










# ....................... LEFT COLUMN: SELECT SPOT  .........................................................
with body_left_col:
    
    #st.subheader("CÓDIGO: 645205")
    
    st.markdown(f'<div align="left"><h1 style="color:#2A4B80; display: inline">{p["left_column"]["title"]}</h1><h5 style="color:#2A4B80; ">CÓDIGO: {p["left_column"]["code"]}</h5></div>', unsafe_allow_html=True)
    
    st.markdown(f'###### {p["left_column"]["platform"]}')
    
    #st.markdown("###### MOINHO DE BOLAS - 5330 MO. 01")
    
    # Lista de itens para escolha
    st.session_state.spot_selected_name = st.radio(label=f'**{p["left_column"]["title_radio"]}**',
                                                   options=spots_list_df["spot_name"])
    
    # Filtra o data frame para apenas a linha que contém o mesmo nome escolhido pelo usuário
    spot_id_selected = spots_list_df.loc[spots_list_df["spot_name"] == st.session_state.spot_selected_name]
    
    # Dentro da do novo data frame, pega apenas o valor que está na coluna spot_id
    st.session_state.spot_id_selected = spot_id_selected["spot_id"].tolist()[0]
    
    csv_file_name = f"spot_{st.session_state.spot_id_selected}.csv"
# ---------------------------------------------------------------------------------------------------------









# ................... GET VARIABLES FROM THE SPOT .........................................................
# Coletas as variáveis disponíves em um dado spot
spot_variables_df_api = fd.fetch_variables_from_spot(st.session_state.spot_id_selected, api_key)

spot_variables_df_custom = fd.csv_for_spot_variables(spot_variables_df_api, csv_file_name)

# ---------------------------------------------------------------------------------------------------------







# ................ CENTRAL COLUMN: PLOTS ...................................................................
with body_center_col:
    
    tab_image, tab_plots, tab_config = st.tabs([p["center_column"]["tabs"]["tab_image"], 
                                                p["center_column"]["tabs"]["tab_plots"], 
                                                p["center_column"]["tabs"]["tab_config"]])
    
    with tab_config:
        st.session_state.user_password = st.text_input(label="Senha de acesso às configurações", type="password")
        
        tab_config_col_1, tab_config_col_2, tab_config_col_3 = st.columns(3)
        
        
        if st.session_state.user_password == st.secrets["senha_config"]:              
            
            with tab_config_col_1:
                st.markdown(f'###### {p["center_column"]["tab_config"]["title"]}')
            
    with tab_image:
        st.image(spot_image, use_column_width=True)
    
    with tab_plots:
        

        
        st.markdown(f"#### {st.session_state.spot_selected_name}")    

        col_radio_select, col_date_interval = st.columns(2)
        
        # date_interval_options ={
        #     1 : "24 horas",
        #     7 : "7 dias",
        #     15 : "15 dias",
        # }
        
        
        
        # date_interval = st.radio(label="Quantidade de dias analisados",
        #                          options=(1, 7, 15),
        #                          format_func= lambda x: date_interval_options.get(x),
        #                          horizontal=True,
        #                          label_visibility="collapsed",
        #                          )
        
        with col_radio_select: 
        
            time_interval_option = st.radio(label="Intervalo de tempo",
                                            options=("24 horas", "Personalizado"),
                                            horizontal=True,
                                            label_visibility="collapsed")

        if time_interval_option == "Personalizado":
            
            with col_date_interval:            
                date_interval = st.date_input(label="Intervalo entre datas", value=(days_ago_7,today))
                if len(date_interval) == 2:
                    start_timestamp, end_timestamp = fd.timestamp_from_date_interval(date_interval)
                    fetch_data_from_date_interval = True
            # with st.form(key="select_date_interval"):
                # col_start_date, col_end_date, col_submit_dates = st.columns(3)                
                # with col_start_date:
                #     start_date = st.date_input(label="Data de Início da Análise", value=days_ago_7)
                
                # with col_end_date:
                #     end_date = st.date_input(label="Data de Término na Análise", value=today)
                
                # with col_submit_dates:
                #     st.markdown("#### ")
                #     date_interval_selected = st.form_submit_button("Enviar", use_container_width=True)    
                
                # date_interval = st.date_input(label="Teste de duas datas", value=(days_ago_7,today))
                # date_interval_selected = st.form_submit_button("Enviar", use_container_width=True)
            
            # if date_interval_selected:
            # st.write(date_interval[0])
            # st.write(date_interval[1])
                # st.success("Solicitação realizada com sucesso. Aguarde")
            
        
        for variable in spot_variables_df_custom["global_data_id"]:

            
            # Coleta dos dados de uma dada variável
            
            if fetch_data_from_date_interval:
                #spot_variables_data_df = fd.fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable)
                spot_variables_data_df = fd.fetch_data_between_dates(spot_id=st.session_state.spot_id_selected,
                                                                     global_data_id=variable,
                                                                     start_timestamp=start_timestamp,
                                                                     end_timestamp=end_timestamp,
                                                                     api_key=api_key)
                
                #spot_variables_data_df = fd.fetch_data_for_time_interval(st.session_state.spot_id_selected, variable, date_interval, api_key)
            else:
                spot_variables_data_df = fd.fetch_data_from_variable_from_spot(st.session_state.spot_id_selected, variable)
            
            # Coleta o nome da variável em questão
            variable_name = spot_variables_df_custom[spot_variables_df_custom["global_data_id"] == variable]["global_data_name"].tolist()[0]
            
            if variable_name == "VELOCIDADE":
                variable_name = "VELOCIDADE - mm/s"
                df_header = ["Vertical", "Horizontal", "Axial", "timestamp"]
            if variable_name == "ACELERAÇÃO":
                variable_name = "ACELERAÇÃO - g"
                df_header = ["Vertical", "Horizontal", "Axial", "timestamp"]
            if variable_name == "TEMPERATURA":
                variable_name = "TEMPERATURA - °C"
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
            
            fig.update_xaxes(range=[0, max_x_value*1.4])
            
            fig.add_vline(x=alarm_alert, line_dash="dash", line_color="gold")
            fig.add_vline(x=alarm_critical, line_dash="dash", line_color="red")

            fig.update_layout(height=number_of_variables*30)
            #fig.update_layout(title=variable_name)
            fig.update_layout(showlegend=False)
            config = {'staticPlot': True}
            
            
            
            fig.update_layout(margin=dict(t=0, b=0))

            fig.update_layout(font=dict(size=16, color="black"))
            
            fig.update_layout(yaxis=dict(tickfont=dict(size=16, color="black")))

            body_left_col.markdown(f"###### {variable_name}")
            body_left_col.plotly_chart(fig, theme="streamlit", use_container_width=True, config = config)
            
            
            f.plot_dataframe_lines(spot_variables_data_df, variable_name, alarm_alert, alarm_critical)
            
            with st.expander("Arquivos para Exportação", expanded=False):
                st.dataframe(spot_variables_data_df, use_container_width=True)
                xlsx_to_download = fd.df_to_xlsx(spot_variables_data_df, variable_name)
                download_xlsx_button = st.download_button(
                    label="Baixar arquivo XLSX",
                    data=xlsx_to_download,
                    file_name=f'{st.session_state.spot_selected_name}-{variable_name}.xlsx',
                    mime='application/vnd.ms-excel'
                    )
                
                csv_for_download = fd.df_to_csv(spot_variables_data_df)
                st.download_button(
                    label="Baixar aquivo CSV",
                    data=csv_for_download,
                    file_name=f'{st.session_state.spot_selected_name}_{variable_name}.csv',
                    mime='text/csv',
                )

            
            with tab_config:
                
                if st.session_state.user_password == st.secrets["senha_config"]:
                
                    with tab_config_col_1:
                        with st.form(key=variable_name):
                            st.markdown(f"###### {variable_name}")
                            alarm_alert_custom = st.number_input(label=p["center_column"]["tab_config"]["alert"], 
                                                                value=alarm_alert,
                                                                key=variable_name+"alarm_alert")
                            
                            alarm_critical_custom = st.number_input(label=p["center_column"]["tab_config"]["critical"], 
                                                                    value=alarm_critical,
                                                                    key=variable_name+"alarm_critical")
                            
                            alarm_settings_changed = st.form_submit_button("Salvar", use_container_width=True)
                            if alarm_settings_changed:
                                spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_alert"] = alarm_alert_custom
                                spot_variables_df_custom.loc[spot_variables_df_custom["global_data_id"] == variable, "alarm_critical"] = alarm_critical_custom
                                spot_variables_df_custom.to_csv(csv_file_name, index=False)
                                st.experimental_rerun()
                
            
        with tab_config_col_2:
            
            if st.session_state.user_password == st.secrets["senha_config"]:
            
                st.markdown(f"###### Textos")
                with st.form(key="params_config"):
                    
                    p["page_config"]["page_title"] = st.text_input(label="Título da Página", value=p["page_config"]["page_title"])
                    
                    p["left_column"]["title"] = st.text_input(label="Barra Lateral: Título", value=p["left_column"]["title"])
                    p["left_column"]["code"] = st.text_input(label="Barra Lateral: Código", value=p["left_column"]["code"])
                    p["left_column"]["platform"] = st.text_input(label="Barra Lateral: Plataforma", value=p["left_column"]["platform"])
                    p["left_column"]["title_radio"] = st.text_input(label="Barra Lateral: Título do Seletor", value=p["left_column"]["title_radio"])
                    
                    p["center_column"]["tabs"]["tab_image"] = st.text_input(label="Título da aba de imagens", value=p["center_column"]["tabs"]["tab_image"])
                    p["center_column"]["tabs"]["tab_plots"] = st.text_input(label="Título da aba de gráficos", value=p["center_column"]["tabs"]["tab_plots"])
                    p["center_column"]["tabs"]["tab_config"] = st.text_input(label="Título da aba de configurações", value=p["center_column"]["tabs"]["tab_config"])
                    
                    p["center_column"]["tab_config"]["title"] = st.text_input(label="Título da seção de alertas", value=p["center_column"]["tab_config"]["title"])
                    p["center_column"]["tab_config"]["alert"] = st.text_input(label="Alarme de Alerta", value=p["center_column"]["tab_config"]["alert"])
                    p["center_column"]["tab_config"]["critical"] = st.text_input(label="Alarme Crítico", value=p["center_column"]["tab_config"]["critical"])
                    params_changed = st.form_submit_button("Salvar", use_container_width=True)
                    if params_changed:
                        fp.save_params(p, params_json_filepath)
                        st.success("Parâmetros alterados com sucesso")
                        st.experimental_rerun()
                        
                st.markdown(f"###### Nomes dos Spots")
                with st.form(key="spots_names"):
                    spots_list_df["spot_name"][0] = st.text_input("Nome do spot 1", value=spots_list_df["spot_name"][0])
                    spots_list_df["spot_name"][1] = st.text_input("Nome do spot 2", value=spots_list_df["spot_name"][1])
                    spots_list_df["spot_name"][2] = st.text_input("Nome do spot 3", value=spots_list_df["spot_name"][2])
                    spots_list_df["spot_name"][3] = st.text_input("Nome do spot 4", value=spots_list_df["spot_name"][3])
                    spot_names_changed = st.form_submit_button("Salvar", use_container_width=True)
                    if spot_names_changed:
                        spots_list_df.to_csv(spots_list_csv, index=False)
                        st.experimental_rerun()
        
        with tab_config_col_3:
            
            if st.session_state.user_password == st.secrets["senha_config"]:
                
                st.markdown(f"###### Imagens")
                with st.form(key="change_my_logo"):
                    st.markdown(f"###### Logo da Empresa")
                    st.image(my_logo, use_column_width=True)
                    my_new_logo = st.file_uploader(label="Envie uma nova imagem", type=['png', 'jpeg', 'jpg'])
                    changed_my_logo = st.form_submit_button("Salvar", use_container_width=True)
                    if changed_my_logo:
                        with open(my_logo, "wb") as f:
                            f.write(my_new_logo.getvalue())
                        st.success("Imagens alteradas com sucesso")
                        st.experimental_rerun()
                
                # with st.form(key="change_client_logo"):
                #     st.markdown(f"###### Logo do Cliente")
                #     st.image(client_logo, use_column_width=True)
                #     client_new_logo = st.file_uploader(label="Envie uma nova imagem", type=['png', 'jpeg', 'jpg'])
                #     changed_client_logo = st.form_submit_button("Salvar", use_container_width=True)
                #     if changed_client_logo:
                #         with open(client_logo, "wb") as f:
                #             f.write(client_new_logo.getvalue())
                #         st.success("Imagens alteradas com sucesso")
                #         st.rerun()

                with st.form(key="change_monitoring_spot"):
                    st.markdown(f"###### Ponto de Monitoramento")
                    st.image(spot_image, use_column_width=True)
                    new_spot_image = st.file_uploader(label="Envie uma nova imagem", type=['png', 'jpeg', 'jpg'])
                    changed_spot_image = st.form_submit_button("Salvar", use_container_width=True)
                    if changed_spot_image:
                        with open(spot_image, "wb") as f:
                            f.write(new_spot_image.getvalue())
                        st.success("Imagens alteradas com sucesso")
                        st.experimental_rerun()


with body_left_col:    
    st.caption(f"Atualizado em {last_timestamp}")               




# while True:
#     time.sleep(600)
#     st.experimental_rerun()


                # st.image("logo_usiminas.png", use_column_width=True)
                # st.image("pontos_monitoramento.png", use_column_width=True)
