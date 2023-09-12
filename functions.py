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

def plot_dataframe_lines(df):
    pass
    df = pd.DataFrame(df)
    columns_list = df.columns.to_list()
    x_column = columns_list[-1]
    y_columns = columns_list[:-1]
    for y_column in y_columns:
        plot_df = df[[x_column, y_column]]
        fig = px.line(plot_df, x=x_column, y=y_column)
        st.plotly_chart(fig, theme="streamlit")
        with st.expander("Visualizar tabela"):
            st.write(plot_df)


