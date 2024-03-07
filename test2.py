import json
from pub_worm.ncbi.entreze_api import EntrezAPI

entrez_api = EntrezAPI()
method_params = {}
method_params['function']='esearch'
method_params['db']='pubmed'
method_params['term']='science[journal] AND breast cancer AND 2008[pdat]'

ret_data = entrez_api.get_ncbi_data(method_params)
pretty_data = json.dumps(ret_data, indent=4)
print(pretty_data)

