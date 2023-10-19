import requests
import streamlit as st
import pandas as pd
import pytz
from pathlib import Path
from datetime import datetime, timedelta
from io import BytesIO
from pyxlsb import open_workbook as open_xlsb
import xlsxwriter
import re


def variable_name_clean(variable_name):
    return re.sub(r'[^A-Za-z0-9]+', '_', variable_name)

def convert_date_time(df):
    df = pd.DataFrame(df)
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='s', origin='unix')
    brt_timezone = pytz.timezone('America/Sao_Paulo')
    df['timestamp'] = df['timestamp'].dt.tz_localize(pytz.utc)
    df['timestamp'] = df['timestamp'].dt.tz_convert(brt_timezone)
    df['timestamp'] = df['timestamp'].dt.tz_localize(None)
    return df

def timestamp_from_date_interval(date_interval):
    start_date_with_minutes = datetime.combine(date_interval[0], datetime.min.time())
    start_timestamp = int(start_date_with_minutes.timestamp())
    end_date_with_minutes = datetime.combine(date_interval[1], datetime.min.time())
    end_timestamp = int(end_date_with_minutes.timestamp())
    return start_timestamp, end_timestamp

def today():
    timezone_br = pytz.timezone('America/Sao_Paulo')
    now_datetime = datetime.now(timezone_br)
    return now_datetime

def n_days_ago(n_days):
    timezone_br = pytz.timezone('America/Sao_Paulo')
    now_datetime = datetime.now(timezone_br)
    n_days_datetime = now_datetime - timedelta(days=n_days)
    return n_days_datetime

def clear_empty_columns(dataframe):
    df = pd.DataFrame(dataframe)
    return df.dropna(axis=1, how="all")


@st.cache_data
def fetch_spots_list(api_key):
    """
    Fetch the list of spots available for this API key.
    
    Args:
        api_key (str): The API key for the installation.
        
    Returns:
        df (pandas dataframe): The Dataframe created with the response for the request of the API.
    
    Details:
        - Access the url https://api.iotebe.com/v2/spot with api-key as parameter.
        - Uses a requests.get to get a response for the request.
        - Open the response as JSON
        - Create a Pandas DataFrame from the JSON
    
    """
    url = "https://api.iotebe.com/v2/spot"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    spots_list_response = requests.get(url, headers=headers)
    spots_list_json = spots_list_response.json()  
    spots_list_df = pd.DataFrame(spots_list_json)
    return spots_list_df

@st.cache_data
def fetch_variables_from_spot(spot_id, api_key):
    """
    Returns the data available for a given spot.
    
    Args:
        spot_id (str): ID of the spot that is being inspected.
    
    Return:
        df (Pandas DataFrame): DataFrame with a variable of that sensor in each line.
    
    Example for one line:
        - global_data_id: 655
        - global_data_name: VELOCIDADE
        - alarm_critical: 5.230
        - alarm_alert: 3.230
        - alarm_status: GREEN
        - disable_alarm: 0
        - trigger_condition: 1
    
    Details:
        - Construct a URL for the API request with the spot_id and api_key.
        - Get a response from the API using requests.get
        - Open the response as a JSON object.
        - Create a Pandas DataFrame from the JSON object.
        - Returns the Pandas DataFrame
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    spots_variables_response = requests.get(url, headers=headers)
    spots_variables_json = spots_variables_response.json()  
    spots_variables_df = pd.DataFrame(spots_variables_json)
    return spots_variables_df

@st.cache_data(ttl=600)
def fetch_data_from_variable_from_spot(spot_id, global_data_id):
    """
    Fetch the data about a variable in that given spot, clean it and return it into a dataframe
    Args:
    """
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



@st.cache_data
def fetch_data_between_dates(spot_id, global_data_id, start_timestamp, end_timestamp, api_key):
    """
    Fetch the data about a variable in that given spot, clean it and return it into a DataFrame with the configurations to create the plot.
    
    Args:
        spot_id (str): The ID of the selected spot
        global_data_id (str): The ID of the variable of that spot to inspect.
        date_interval (int): Number of days from now to inspect.
    
    Returns:
        df (Pandas DataFrame): Cleaned DataFrame with the data of that time interval.
        
    Details:
        - Create the URL to request the API
        - Get the timezone of Brazil
        - Get the timestamp from now in Brazil timezone
        - Use timedelta to get the timestamp of the start date
        - Do the request with the start and end date as parameters
        - Get the JSON from the response
        - Turn the JSON into pandas DataFrame
        - Convert the datetime columns to datetime type
        - Clear empty columns
        - Return the DataFrame
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    
    
    querystring = {"start_date": str(start_timestamp), "end_date": str(end_timestamp)}
    
    headers = {
    "x-api-key": api_key,
    "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=querystring)
    spot_variable_data_info = response.json()
    spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
    spot_variable_data_df = convert_date_time(spot_variable_data_df)
    spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
    return spot_variable_data_df_clean






@st.cache_data(ttl=600)
def fetch_data_for_time_interval(spot_id, global_data_id, date_interval, api_key):
    """
    Fetch the data about a variable in that given spot, clean it and return it into a DataFrame with the configurations to create the plot.
    
    Args:
        spot_id (str): The ID of the selected spot
        global_data_id (str): The ID of the variable of that spot to inspect.
        date_interval (int): Number of days from now to inspect.
    
    Returns:
        df (Pandas DataFrame): Cleaned DataFrame with the data of that time interval.
        
    Details:
        - Create the URL to request the API
        - Get the timezone of Brazil
        - Get the timestamp from now in Brazil timezone
        - Use timedelta to get the timestamp of the start date
        - Do the request with the start and end date as parameters
        - Get the JSON from the response
        - Turn the JSON into pandas DataFrame
        - Convert the datetime columns to datetime type
        - Clear empty columns
        - Return the DataFrame
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    
    timezone_br = pytz.timezone('America/Sao_Paulo')
    
    now_datetime = datetime.now(timezone_br)
    
    start_datetime = now_datetime - timedelta(days=date_interval)
    
    now_timestamp = int(now_datetime.timestamp())
    
    start_timestamp = int(start_datetime.timestamp())

    
    querystring = {"start_date": str(start_timestamp), "end_date": str(now_timestamp)}
    
    headers = {
    "x-api-key": api_key,
    "Accept": "application/json"
    }
    response = requests.get(url, headers=headers, params=querystring)
    spot_variable_data_info = response.json()
    spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
    spot_variable_data_df = convert_date_time(spot_variable_data_df)
    spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
    return spot_variable_data_df_clean




def csv_for_spot_variables(spot_variables_df_api, csv_file_name):
    """
    Check if the ir or not a CSV file with the data of an spot and create one if not.
    It is important for the user customized alarm limits.
    
    Args:
        spot_variables_df_api (Pandas DataFrame): The DataFrame without cleaning.
        csv_file_name (str): Name of the CSV file to check.
    
    Return:
        df (Pandas DataFrame): DataFrame cleaned and saved into the CSV.
    
    Details:
        - Get the dirty DataFrame
        - Clean the DataFrame taking out the RMS variables
        - Check if there is a CSV for that spot.
        - Read the CSV if it exists and create one if not.
        - Return the clean DataFrame with users alarm settings.
    
    """
    spot_variables_df_api = pd.DataFrame(spot_variables_df_api)
    
    spot_variables_df_api = spot_variables_df_api.dropna(subset=['alarm_critical'])

    csv_file_path = Path(csv_file_name)

    if csv_file_path.is_file():
        pass
    else:
        spot_variables_df_api.to_csv(csv_file_name, index=False)

    spot_variables_df_custom = pd.read_csv(csv_file_name)
    
    return spot_variables_df_custom
    
def csv_for_spot_list(spots_list_api, csv_file_name):
    """
    Check if the ir or not a CSV file with the data of an spot and create one if not.
    It is important for the user customized alarm limits.
    
    Args:
        spot_variables_df_api (Pandas DataFrame): The DataFrame without cleaning.
        csv_file_name (str): Name of the CSV file to check.
    
    Return:
        df (Pandas DataFrame): DataFrame cleaned and saved into the CSV.
    
    Details:
        - Get the dirty DataFrame
        - Clean the DataFrame taking out the RMS variables
        - Check if there is a CSV for that spot.
        - Read the CSV if it exists and create one if not.
        - Return the clean DataFrame with users alarm settings.
    
    """
    spots_list_api = pd.DataFrame(spots_list_api)

    csv_file_path = Path(csv_file_name)

    if csv_file_path.is_file():
        pass
    else:
        spots_list_api.to_csv(csv_file_name, index=False, encoding="utf-8")

    spot_variables_df_custom = pd.read_csv(csv_file_name)
    
    return spot_variables_df_custom




@st.cache_data
def to_excel(df, spot_selected, variable_name):
    sheet_name = f'{spot_selected}-{variable_name}'
    df = pd.DataFrame(df)
    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')
    df.to_excel(writer, index=False, sheet_name=sheet_name)
    workbook = writer.book
    worksheet = writer.sheets[sheet_name]
    writer.save()
    processed_data = output.getvalue()
    return processed_data

@st.cache_data
def df_to_xlsx(df, variable_name):
    buffer = BytesIO()
    df = pd.DataFrame(df)
    sheet_name = variable_name_clean(variable_name)
    with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
        writer.close()
        processed_data = buffer.getvalue()
        return processed_data
    
@st.cache_data
def df_to_csv(df):
    df = pd.DataFrame(df)
    return df.to_csv(index=False).encode('utf-8')


    





    
