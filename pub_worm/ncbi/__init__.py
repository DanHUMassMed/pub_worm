import json
import pkgutil

# Load the JSON data from the file
def load_ncbi_api_json(function):
    data_bytes = pkgutil.get_data(__name__, f"data/ncbi_{function}.json")
    data_str = data_bytes.decode('utf-8')
    return json.loads(data_str)
