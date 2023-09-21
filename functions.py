import requests
import streamlit as st
import pandas as pd
import pytz
import plotly.express as px

def convert_date_time(df):
    df = pd.DataFrame(df)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', origin='unix')
    brt_timezone = pytz.timezone('America/Sao_Paulo')
    df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.utc)
    df['timestamp'] = df['timestamp'].dt.tz_convert(brt_timezone)
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    return df
    

def clear_empty_columns(dataframe):
    df = pd.DataFrame(dataframe)
    return df.dropna(axis=1, how="all")

@st.cache_data
def fetch_spots_list():
    url = "https://api.iotebe.com/v2/spot"
    headers = {
        "x-api-key": st.secrets["chave_api"],
        "Accept": "application/json"
    }
    spots_list_response = requests.get(url, headers=headers)
    spots_list_json = spots_list_response.json()  
    spots_list_df = pd.DataFrame(spots_list_json)
    return spots_list_df

@st.cache_data
def fetch_variables_from_spot(spot_id):
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data"
    headers = {
        "x-api-key": st.secrets["chave_api"],
        "Accept": "application/json"
    }
    spots_variables_response = requests.get(url, headers=headers)
    spots_variables_json = spots_variables_response.json()  
    spots_variables_df = pd.DataFrame(spots_variables_json)
    return spots_variables_df

@st.cache_data(ttl=600)
def fetch_data_from_variable_from_spot(spot_id, global_data_id):
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    headers = {
    "x-api-key": st.secrets["chave_api"],
    "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    spot_variable_data_info = response.json()
    spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
    spot_variable_data_df = convert_date_time(spot_variable_data_df)
    spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
    return spot_variable_data_df_clean

# def plot_dataframe_lines(df):
#     df = pd.DataFrame(df)
#     columns_list = df.columns.to_list()
#     x_column = columns_list[-1]
#     y_columns = columns_list[:-1]
#     for y_column in y_columns:
#         plot_df = df[[x_column, y_column]]
#         fig = px.line(plot_df, x=x_column, y=y_column)
#         st.plotly_chart(fig, theme="streamlit")
#         with st.expander("Visualizar tabela"):
#             st.write(plot_df)


def plot_dataframe_lines(df, variable_name, alarm_alert, alarm_critical):
    df = pd.DataFrame(df)
    columns_list = df.columns.to_list()
    x_column = columns_list[-1]
    y_columns = columns_list[:-1]
    fig = px.line(df, x=x_column, y=y_columns)
    
    fig.add_shape(
        type="line",
        x0=df[x_column].min(),
        x1=df[x_column].max(),
        y0=alarm_alert,
        y1=alarm_alert,
        line=dict(color="orange", dash="dash"),
        name=f'Linha Constante ({alarm_alert})')
    
    fig.add_shape(
        type="line",
        x0=df[x_column].min(),
        x1=df[x_column].max(),
        y0=alarm_critical,
        y1=alarm_critical,
        line=dict(color="red", dash="dash"),
        name=f'Linha Constante ({alarm_critical})')

    fig.update_layout(legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1,
        title=""
    ))

    
    fig.update_layout(
        title=variable_name,
        xaxis_title='Data e Hora',
        yaxis_title=variable_name, # Trocar 
        height=250,
    )
    
    
    st.plotly_chart(fig, theme="streamlit", use_container_width=True)


def force_sidebar():
    st.markdown(
        """
    <style>
        [data-testid="baseButton-header"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)
    
def remove_header():
    st.markdown(
        """
    <style>
        [data-testid="stHeader"] {
            display: none
        }
    </style>
    """,
        unsafe_allow_html=True)

def remove_top_padding():
    st.markdown(
        """
    <style>
        [data-testid="block-container"] {
            top: -80px;
        }
        
    </style>
    """,
        unsafe_allow_html=True)
    

