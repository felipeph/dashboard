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
import time


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
    #today_datetime = now_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    today_date = now_datetime.date()
    return today_date

def n_days_ago(n_days):
    timezone_br = pytz.timezone('America/Sao_Paulo')
    now_datetime = datetime.now(timezone_br)
    n_days_datetime = now_datetime - timedelta(days=n_days)
    #n_days_datetime = n_days_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
    n_days_date = n_days_datetime.date()
    return n_days_date

def clear_empty_columns(dataframe):
    df = pd.DataFrame(dataframe)
    return df.dropna(axis=1, how="all")


# @st.cache_data
# def fetch_spots_list(api_key):
#     """
#     Fetch the list of spots available for this API key.
    
#     Args:
#         api_key (str): The API key for the installation.
        
#     Returns:
#         df (pandas dataframe): The Dataframe created with the response for the request of the API.
    
#     Details:
#         - Access the url https://api.iotebe.com/v2/spot with api-key as parameter.
#         - Uses a requests.get to get a response for the request.
#         - Open the response as JSON
#         - Create a Pandas DataFrame from the JSON
    
#     """
#     url = "https://api.iotebe.com/v2/spot"
#     headers = {
#         "x-api-key": api_key,
#         "Accept": "application/json"
#     }
#     spots_list_response = requests.get(url, headers=headers)
#     spots_list_json = spots_list_response.json()  
#     spots_list_df = pd.DataFrame(spots_list_json)
#     return spots_list_df


@st.cache_data
def fetch_spots_list(api_key):
    """
    Fetch the list of spots available for this API key.
    
    Args:
        api_key (str): The API key for the installation.
        
    Returns:
        df (pandas dataframe): The DataFrame created with the response for the request of the API.
    
    Details:
        - Access the URL https://api.iotebe.com/v2/spot with api-key as a parameter.
        - Uses a requests.get to get a response for the request.
        - Checks if the response status code is 200 (OK) before proceeding.
        - Open the response as JSON.
        - Create a Pandas DataFrame from the JSON.
        
    Raises:
        ValueError: If the API request is unsuccessful or the response cannot be converted to JSON.
    """
    url = "https://api.iotebe.com/v2/spot"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    try:
        spots_list_response = requests.get(url, headers=headers)
        spots_list_response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        spots_list_json = spots_list_response.json()
        spots_list_df = pd.DataFrame(spots_list_json)
        return spots_list_df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching data from API: {e}")
    except Exception as e:
        raise ValueError(f"Error converting API response to DataFrame: {e}")



# @st.cache_data
# def fetch_variables_from_spot(spot_id, api_key):
#     """
#     Returns the data available for a given spot.
    
#     Args:
#         spot_id (str): ID of the spot that is being inspected.
    
#     Return:
#         df (Pandas DataFrame): DataFrame with a variable of that sensor in each line.
    
#     Example for one line:
#         - global_data_id: 655
#         - global_data_name: VELOCIDADE
#         - alarm_critical: 5.230
#         - alarm_alert: 3.230
#         - alarm_status: GREEN
#         - disable_alarm: 0
#         - trigger_condition: 1
    
#     Details:
#         - Construct a URL for the API request with the spot_id and api_key.
#         - Get a response from the API using requests.get
#         - Open the response as a JSON object.
#         - Create a Pandas DataFrame from the JSON object.
#         - Returns the Pandas DataFrame
#     """
#     url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data"
#     headers = {
#         "x-api-key": api_key,
#         "Accept": "application/json"
#     }
#     spots_variables_response = requests.get(url, headers=headers)
#     spots_variables_json = spots_variables_response.json()  
#     spots_variables_df = pd.DataFrame(spots_variables_json)
#     return spots_variables_df



@st.cache_data
def fetch_variables_from_spot(spot_id, api_key):
    """
    Returns the data available for a given spot.
    
    Args:
        spot_id (str): ID of the spot that is being inspected.
    
    Returns:
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
        - Get a response from the API using requests.get.
        - Checks if the response status code is 200 (OK) before proceeding.
        - Open the response as a JSON object.
        - Create a Pandas DataFrame from the JSON object.
        - Returns the Pandas DataFrame.
        
    Raises:
        ValueError: If the API request is unsuccessful or the response cannot be converted to JSON.
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data"
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    try:
        spots_variables_response = requests.get(url, headers=headers)
        spots_variables_response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        spots_variables_json = spots_variables_response.json()
        spots_variables_df = pd.DataFrame(spots_variables_json)
        return spots_variables_df
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching data from API: {e}")
    except Exception as e:
        raise ValueError(f"Error converting API response to DataFrame: {e}")




# @st.cache_data(ttl=600)
# def fetch_data_from_variable_from_spot(spot_id, global_data_id):
#     """
#     Fetch the data about a variable in that given spot, clean it and return it into a dataframe
#     Args:
#     """
#     url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
#     headers = {
#     "x-api-key": st.secrets["chave_api"],
#     "Accept": "application/json"
#     }
#     response = requests.get(url, headers=headers)
#     spot_variable_data_info = response.json()
#     spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
#     spot_variable_data_df = convert_date_time(spot_variable_data_df)
#     spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
#     return spot_variable_data_df_clean


@st.cache_data
def fetch_data_from_variable_from_spot(spot_id, global_data_id):
    """
    Fetch the data about a variable in that given spot, clean it, and return it as a DataFrame.
    
    Args:
        spot_id (str): The ID of the selected spot.
        global_data_id (str): The ID of the variable of that spot to inspect.
    
    Returns:
        df (Pandas DataFrame): Cleaned DataFrame with the data.
        
    Details:
        - Construct a URL for the API request.
        - Get the response from the API using requests.get.
        - Checks if the response status code is 200 (OK) before proceeding.
        - Get the JSON from the response.
        - Turn the JSON into a pandas DataFrame.
        - Convert the datetime columns to datetime type.
        - Clear empty columns.
        - Return the DataFrame.
        
    Raises:
        ValueError: If the API request is unsuccessful or the response cannot be converted to DataFrame.
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    
    headers = {
        "x-api-key": st.secrets["chave_api"],
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        spot_variable_data_info = response.json()
        spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
        spot_variable_data_df = convert_date_time(spot_variable_data_df)
        spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
        return spot_variable_data_df_clean
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching data from API: {e}")
    except Exception as e:
        raise ValueError(f"Error converting API response to DataFrame: {e}")




# @st.cache_data
# def fetch_data_between_dates(spot_id, global_data_id, start_timestamp, end_timestamp, api_key):
#     """
#     Fetch the data about a variable in that given spot, clean it and return it into a DataFrame with the configurations to create the plot.
    
#     Args:
#         spot_id (str): The ID of the selected spot
#         global_data_id (str): The ID of the variable of that spot to inspect.
#         date_interval (int): Number of days from now to inspect.
    
#     Returns:
#         df (Pandas DataFrame): Cleaned DataFrame with the data of that time interval.
        
#     Details:
#         - Create the URL to request the API
#         - Get the timezone of Brazil
#         - Get the timestamp from now in Brazil timezone
#         - Use timedelta to get the timestamp of the start date
#         - Do the request with the start and end date as parameters
#         - Get the JSON from the response
#         - Turn the JSON into pandas DataFrame
#         - Convert the datetime columns to datetime type
#         - Clear empty columns
#         - Return the DataFrame
#     """
#     url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    
    
#     querystring = {"start_date": str(start_timestamp), "end_date": str(end_timestamp)}
    
#     headers = {
#     "x-api-key": api_key,
#     "Accept": "application/json"
#     }
#     response = requests.get(url, headers=headers, params=querystring)
#     spot_variable_data_info = response.json()
#     spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
#     spot_variable_data_df = convert_date_time(spot_variable_data_df)
#     spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
#     return spot_variable_data_df_clean



@st.cache_data
def fetch_data_between_dates(spot_id, global_data_id, start_timestamp, end_timestamp, api_key):
    """
    Fetch the data about a variable in that given spot, clean it and return it into a DataFrame with the configurations to create the plot.
    
    Args:
        spot_id (str): The ID of the selected spot.
        global_data_id (str): The ID of the variable of that spot to inspect.
        start_timestamp (str): The start timestamp for the data retrieval.
        end_timestamp (str): The end timestamp for the data retrieval.
        api_key (str): The API key for the installation.
    
    Returns:
        df (Pandas DataFrame): Cleaned DataFrame with the data of that time interval.
        
    Details:
        - Create the URL to request the API.
        - Get the response from the API using requests.get.
        - Checks if the response status code is 200 (OK) before proceeding.
        - Get the JSON from the response.
        - Turn the JSON into a pandas DataFrame.
        - Convert the datetime columns to datetime type.
        - Clear empty columns.
        - Return the DataFrame.
        
    Raises:
        ValueError: If the API request is unsuccessful or the response cannot be converted to DataFrame.
    """
    url = f"https://api.iotebe.com/v2/spot/{spot_id}/ng1vt/global_data/{global_data_id}/data"
    
    querystring = {"start_date": str(start_timestamp), "end_date": str(end_timestamp)}
    
    headers = {
        "x-api-key": api_key,
        "Accept": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers, params=querystring)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx or 5xx)
        
        spot_variable_data_info = response.json()
        spot_variable_data_df = pd.DataFrame(spot_variable_data_info)
        spot_variable_data_df = convert_date_time(spot_variable_data_df)
        spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
        return spot_variable_data_df_clean
    except requests.exceptions.RequestException as e:
        raise ValueError(f"Error fetching data from API: {e}")
    except Exception as e:
        raise ValueError(f"Error converting API response to DataFrame: {e}")





@st.cache_data
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


@st.cache_data
def fetch_data_last_30_days(spot_id, global_data_id, api_key):
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
    
    first_15_days_start_datetime = now_datetime - timedelta(days=15)
    first_15_days_end_timestamp = int(now_datetime.timestamp())
    first_15_days_start_timestamp = int(first_15_days_start_datetime.timestamp())
    
    querystring = {"start_date": str(first_15_days_start_timestamp), 
                   "end_date": str(first_15_days_end_timestamp)}
    
    headers = {
    "x-api-key": api_key,
    "Accept": "application/json"
    }
    
    first_15_days_response = requests.get(url, headers=headers, params=querystring)
    
    first_15_days_json = first_15_days_response.json()
    first_15_days_df = pd.DataFrame(first_15_days_json)
    
    last_15_days_end_datetime = first_15_days_start_datetime
    last_15_days_end_timestamp = int(last_15_days_end_datetime.timestamp())
    
    last_15_days_start_datetime = last_15_days_end_datetime - timedelta(days=15)
    last_15_days_start_timestamp = int(last_15_days_start_datetime.timestamp())
    
    
    querystring = {"start_date": str(last_15_days_start_timestamp), 
                   "end_date": str(last_15_days_end_timestamp)}
    
    headers = {
    "x-api-key": api_key,
    "Accept": "application/json"
    }
    
    last_15_days_response = requests.get(url, headers=headers, params=querystring)
    last_15_days_json = last_15_days_response.json()
    last_15_days_df = pd.DataFrame(last_15_days_json)    
    
    last_30_days_df = pd.merge(last_15_days_df, first_15_days_df, how="outer")
    
    
    spot_variable_data_df = pd.DataFrame(last_30_days_df)
    spot_variable_data_df = convert_date_time(spot_variable_data_df)
    spot_variable_data_df_clean = clear_empty_columns(spot_variable_data_df)
    return spot_variable_data_df_clean




def csv_for_spot_variables(spot_variables_df_api, csv_file_name):
    """
    Check if the is or not a CSV file with the data of an spot and create one if not.
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

@st.cache_data
def calculate_time_elapsed(df):
    df = pd.DataFrame(df)
    if 'timestamp' not in df.columns:
        raise ValueError("The DataFrame must contain a 'timestamp' column.")

    df_sorted = df.sort_values('timestamp')

    # Get the first and last timestamps
    first_timestamp = df_sorted['timestamp'].iloc[0]
    last_timestamp = df_sorted['timestamp'].iloc[-1]

    # Calculate the time difference
    time_elapsed = last_timestamp - first_timestamp

    return time_elapsed

@st.cache_data    
def sum_values_except_timestamp(df):
    df = pd.DataFrame(df)
    
    # Check if 'timestamp' column is present
    if 'timestamp' not in df.columns:
        raise ValueError("The DataFrame must contain a 'timestamp' column.")

    # Sum all columns except 'timestamp'
    sum_result = df.drop(columns=['timestamp']).sum(axis=1)

    # Create a new DataFrame with the timestamp and the sum result
    sum_df = pd.DataFrame({'timestamp': df['timestamp'], 
                              'sum_values': sum_result})

    return sum_df

@st.cache_data
def calculate_time_diff(df):
    df = pd.DataFrame(df)
    
    # Assuming 'timestamp' is the name of your datetime column
    if 'timestamp' not in df.columns:
        raise ValueError("The DataFrame must contain a 'timestamp' column.")

    # Sort the DataFrame by the 'timestamp' column
    df_sorted = df.sort_values('timestamp')

    # Calculate the time difference between consecutive records
    time_diff = df_sorted['timestamp'].diff()

    # Convert time differences to seconds 
    time_diff_seconds = time_diff.dt.total_seconds()

    # Create a new column with the time differences in seconds
    df_sorted['time_diff'] = time_diff_seconds

    return df_sorted

@st.cache_data
def total_time_above_or_below_minimum(df, minimum_value):
    df = pd.DataFrame(df)
    
    if 'timestamp' not in df.columns or 'sum_values' not in df.columns or 'time_diff' not in df.columns:
        raise ValueError("The DataFrame must contain 'timestamp', 'sum_values', and 'time_diff' columns.")

    # Filter records based on the minimum value
    above_min_value = df[df['sum_values'] > minimum_value]
    below_min_value = df[df['sum_values'] <= minimum_value]

    # Calculate the total time difference for records above the minimum value
    total_time_diff_above_min = above_min_value['time_diff'].sum() / 3600

    # Calculate the total time difference for records below or equal to the minimum value
    total_time_diff_below_min = below_min_value['time_diff'].sum() / 3600

    return total_time_diff_above_min, total_time_diff_below_min

@st.cache_data
def count_failures(dataframe, min_value):
    """
    Count the number of failure events in a DataFrame based on a specified minimum value.

    Parameters:
    - dataframe (pd.DataFrame): The input DataFrame containing a 'timestamp' column and a 'sum_values' column.
    - min_value (float, optional): The minimum value used to define failure events.

    Returns:
    - int: The total number of failure events in the DataFrame.
    """

    dataframe = pd.DataFrame(dataframe)
    # Add a column indicating if there is a failure
    dataframe['failure'] = dataframe['sum_values'] < min_value
    
    # Filter only the points where "failure" is true
    fail_df = dataframe[dataframe['failure']]
    
    # Add a column indicating the start of a failure
    dataframe['failure_shifted'] = dataframe['failure'].shift()
    dataframe['failure_shifted_inverted'] = dataframe['failure_shifted'] == False
    dataframe['failure_start'] = dataframe['failure'] & dataframe['failure_shifted_inverted']
    
    # Count how many times the value True appears in the 'failure_start' column
    total_failures = dataframe['failure_start'].sum()
    
    return total_failures


def read_reliability_csv(csv_filename):
    reliability_df = pd.read_csv(csv_filename)
    reliability_df['start_date'] = pd.to_datetime(reliability_df['start_date'])
    reliability_df['end_date'] = pd.to_datetime(reliability_df['end_date'])
    reliability_df['start_date'] = reliability_df['start_date'].dt.date
    reliability_df['end_date'] = reliability_df['end_date'].dt.date    
    return reliability_df

@st.cache_data
def get_reliability_end_date(df):
    end_date = df['end_date'][0]
    return end_date


@st.cache_data
def get_reliability_start_date(df):
    start_date = df['start_date'][0]
    return start_date

