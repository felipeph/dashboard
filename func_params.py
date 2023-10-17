import json

def load_params(filepath):
    """
    Loads the params dictionary from a JSON file.
    """
    try:
        with open(filepath, encoding='utf-8') as file:
            params_dict = json.load(file)
    except Exception as e:
        print(f"Caught an exception: {type(e).__name__} - {e}")
    return params_dict

def save_params(params_dict, filepath):
    """
    Save the params dictionary into a JSON file.
    """
    try:
        with open(filepath, mode="w", encoding='utf-8') as file:
            json.dump(params_dict, file, indent=4)
    except Exception as e:
        print(f"Caught an exception: {type(e).__name__} - {e}")