import streamlit as st
import func_data as fd
import plotly.express as px
import pandas as pd
import plotly.graph_objects as go



api_key = st.secrets["chave_api"]


with st.expander(label="Teste de coleta de 15 dias", expanded=True):
    last_30_days_df = fd.fetch_data_last_30_days(spot_id=219, global_data_id=655, api_key=api_key)
    st.dataframe(last_30_days_df)
    summed_df = fd.sum_values_except_timestamp(last_30_days_df)
    st.dataframe(summed_df)
    fig_raw_summed_df = px.line(summed_df, x="timestamp", y="sum_values")
    st.plotly_chart(figure_or_data=fig_raw_summed_df, use_container_width=True)

    # # Calcular a média móvel com uma janela de, por exemplo, 7 dias
    # summed_df['media_movel'] = summed_df['sum_values'].rolling(window=20).mean()
    # st.dataframe(summed_df)
    
    # # Criar um gráfico de linha interativo
    # fig_mean = px.line(summed_df, x='timestamp', y=['sum_values', 'media_movel'],
    #             labels={'timestamp': 'Timestamp', 'value': 'Valor'},
    #             title='Gráfico de Linha: Sum_Values e Média Móvel')
    
    # st.plotly_chart(figure_or_data=fig_mean, use_container_width=True)


    # Adicionando uma coluna indicando se há uma falha
    summed_df['falha'] = summed_df['sum_values'] < 0.8


    st.dataframe(summed_df, use_container_width=True)
    
    falha_df = summed_df[summed_df['falha']]

    # Criar um gráfico de pontos interativo
    fig_falha = px.scatter(falha_df, x='timestamp', y='sum_values',
                    title='Gráfico de Pontos para Valores de Falha',
                    labels={'timestamp': 'Timestamp', 'sum_values': 'Sum_Values'},
                    color='falha',  # Colorir pontos com base na coluna "falha"
                    color_discrete_map={True: 'red', False: 'blue'}  # Mapear cores para valores de "falha"
                    )
    
    st.plotly_chart(fig_falha, use_container_width=True)
    
    
    summed_df['falha_shiffed'] = summed_df['falha'].shift()
    
    st.dataframe(summed_df, use_container_width=True)

    summed_df['falha_shiffed_inverted'] = summed_df['falha_shiffed'] == False
    
    st.dataframe(summed_df, use_container_width=True)

    summed_df['falha_inicio'] = summed_df['falha'] & summed_df['falha_shiffed_inverted']
    
    st.dataframe(summed_df, use_container_width=True)
    
    quantidade_de_falhas = summed_df['falha_inicio'].sum()
    
    st.write(quantidade_de_falhas)
    
    # summed_df['falha_inicio'] = summed_df['falha'] & ~summed_df['falha'].shift()

    st.dataframe(summed_df, use_container_width=True)
    
    # Filtrar apenas os pontos onde "falha_inicio" é verdadeiro
    falha_inicio_df = summed_df[summed_df['falha_inicio']]

    # Criar um gráfico de dispersão interativo
    fig_falha_inicio = px.scatter(falha_inicio_df, x='timestamp', y='sum_values',
                    title='Pontos com Início de Falha',
                    labels={'timestamp': 'Timestamp', 'sum_values': 'Sum_Values'},
                    color='falha_inicio',  # Colorir pontos com base na coluna "falha_inicio"
                    color_discrete_map={True: 'red'}  # Mapear cor para valores de "falha_inicio" verdadeiros
                    )
    
    st.plotly_chart(figure_or_data=fig_falha_inicio, use_container_width=True)


    fig_falha_inicio.add_trace(go.Scatter(x=fig_raw_summed_df.data[0]['x'], 
                                        y=fig_raw_summed_df.data[0]['y'],
                                        mode='lines', name='Raw Sum_Values'))

    st.plotly_chart(figure_or_data=fig_falha_inicio, use_container_width=True)
    
    # Criar um gráfico de linha interativo com destaque para os períodos de falha
    # fig_fail_detect = px.line(summed_df, x='timestamp', y='sum_values',
    #             title='Gráfico de Linha com Detecção de Falha')

    # # Adicionar uma linha horizontal para indicar o limite de falha
    # fig_fail_detect.add_shape(
    #     type='line',
    #     x0=summed_df['timestamp'].min(),
    #     x1=summed_df['timestamp'].max(),
    #     y0=0.8,
    #     y1=0.8,
    #     line=dict(color='red', dash='dash'),
    # )

    # # Adicionar marcações para os períodos de falha
    # for i, row in summed_df[summed_df['falha']].iterrows():
    #     fig_fail_detect.add_shape(
    #         type='rect',
    #         x0=row['timestamp'],
    #         x1=row['timestamp'],
    #         y0=summed_df['sum_values'].min(),
    #         y1=summed_df['sum_values'].max(),
    #         fillcolor='red',
    #         opacity=0.3,
    #         layer='below',
    #     )

    # st.plotly_chart(figure_or_data=fig_fail_detect, use_container_width=True)

    # time_diff_df = fd.calculate_time_diff(summed_df)
    # st.dataframe(time_diff_df)
    # time_working, time_stopped = fd.total_time_above_or_below_minimum(time_diff_df, 1)
    # st.write(time_working)
    # st.write(time_stopped)