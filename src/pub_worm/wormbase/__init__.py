import json
import pkgutil

# Load the JSON data from the file
def load_wormbase_api_json(call_type, call_class):
    data_bytes = pkgutil.get_data(__name__, f"data/wormbase_{call_type}_{call_class}.json")
    data_str = data_bytes.decode('utf-8')
    return json.loads(data_str)
