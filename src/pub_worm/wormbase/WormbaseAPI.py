'''
WormbaseREST REST API for http://rest.wormbase.org/index.html
'''
import time
import json
import pandas as pd
import urllib.request
import logging
import logging.config
from pub_worm.wormbase import load_wormbase_api_json

logging.config.fileConfig('logging.config')
# Create a logger object
logger = logging.getLogger(__name__)

class WormbaseAPI:

    def __init__(self):
        self.base_url_str = f"https://wormbase.org/rest"

    def rest_api_call(self, call_type, call_class, object_id, data_request):
        url_str = f"{self.base_url_str}/{call_type}/{call_class}/{object_id}/{data_request}"

        max_retries = 3
        retry = 0
        done = False

        api_result = None
        api_error = None

        def handle_error(error_msg):
            print(error_msg)
            nonlocal done, retry, api_error
            if retry >= max_retries:
                done = True
                api_error = error_msg

        while not done:
            try:
                url = urllib.request.urlopen(url_str)
                if url.getcode() == 429:
                    handle_error(f"eUtilsGet: Request limiter hit. [Retry: {retry + 1}] code: {url.getcode()}")
                    time.sleep(2)
                elif url.getcode() == 200:
                    done = True
                    response_text = url.read().decode('utf-8')
                    api_result = json.loads(response_text)
                else:
                    handle_error(f"restAPICall- Failed to retrieve data. | Retry- {retry + 1} | Response code- {url.getcode()}")
            except Exception as ex:
                handle_error(f"restAPICall- Check if you have a connection!! | Retry- {retry + 1} | Response msg- {str(ex)}")

        if api_result is None:
            api_result = {"rest_api_error": api_error}
        
        if logger.isEnabledFor(logging.DEBUG):
            pretty_data = json.dumps(api_result, indent=4)
            with open('http_response.json', 'w') as file:
                file.write(pretty_data)
            #logger.debug(pretty_data)
            

        return api_result

    def get_json_element(self, json_data, path):
        result = json_data
        try:
            for key in path:
                result = result[key]
        except Exception: #KeyError TypeError
            result = None
        return result


    def extract_single_element_lists(self, json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                json_obj[key] = self.extract_single_element_lists(value)
        elif isinstance(json_obj, list):
            # If list length is 1 remove list
            if len(json_obj) == 1:
                return self.extract_single_element_lists(json_obj[0])
            else:
                return [self.extract_single_element_lists(item) for item in json_obj]
        return json_obj


    def get_wormbase_data(self, method_params):
        call_type = method_params["call_type"]
        call_class = method_params["call_class"]
        object_id = method_params["object_id"]
        data_request = method_params["data_request"]
        get_json = self.get_json_element

        if object_id is None:
            raise Exception("objectID cannot be null!")
    
        rest_api_call_results = self.rest_api_call(call_type, call_class, object_id, data_request)
        if "rest_api_error" in rest_api_call_results:
            return ret_dict

        ret_dict = {}
        wormbase_api_json = load_wormbase_api_json(call_type, call_class)
        if data_request not in wormbase_api_json:
            logger.error(f"No wormbase connfig for {data_request=}")
            return {}
        results_doc_definition = wormbase_api_json[data_request]

        def parse_data(data_to_process, doc_definition, results_dict):
            # data_request_item_nm="description" data_request_item=["fields", "concise_description","data","text"]
            # data_request_item_nm="author"      data_request_item={ "ROOT": ["author"], "CONCAT": ["label"] }
            for data_request_item_nm, data_request_item in doc_definition.items():
                logger.debug(f"{data_request_item_nm=}{data_request_item=}")
                if isinstance(data_request_item, list):
                    data_request_item_path = data_request_item
                    widget_item = get_json(data_to_process, data_request_item_path)
                    if widget_item is not None:
                        results_dict[data_request_item_nm] = widget_item
                elif isinstance(data_request_item, dict):
                    logger.debug(f"BEFORE {data_request_item=}, {data_request_item['ROOT']=}")
                    pretty_data = json.dumps(data_to_process, indent=4)
                    #logger.debug(f"BEFORE {pretty_data}")
                    sub_data_to_process = get_json(data_to_process, data_request_item["ROOT"])
                    if sub_data_to_process is None:
                        logger.debug(f"AFTER WTF")

                    if sub_data_to_process is not None:
                        pretty_data = json.dumps(sub_data_to_process, indent=4)
                        #logger.debug(f"AFTER {pretty_data}")
                        if "CONCAT" in data_request_item:
                            sub_results_str = ""
                            for sub_data_item in sub_data_to_process:
                                sub_results = parse_data(sub_data_item, data_request_item, {})
                                if "CONCAT" in sub_results:
                                    sub_results_str +=str(f"{sub_results['CONCAT']}|")
                            results_dict[data_request_item_nm] = sub_results_str[:-1]
                            logger.debug(f"Found CONCAT")
                        else:
                            logger.debug(f"AFTER NO CONCAT")
                            if isinstance(sub_data_to_process, dict):
                                logger.debug(f"DICT {sub_data_to_process=}")
                                logger.debug(f"DICT {data_request_item=}")
                                results_dict[data_request_item_nm] = parse_data(sub_data_to_process, data_request_item, {})
                            else: #It is a list
                                sub_results_list = []
                                for sub_data_item in sub_data_to_process:
                                    logger.debug(f"ITS a LIST {sub_data_item}")
                                    sub_results_list.append(parse_data(sub_data_item, data_request_item, {}))
                                results_dict[data_request_item_nm] = sub_results_list

                else:
                    logger.debug("!!"*40)

            results_dict = self.extract_single_element_lists(results_dict)
            return results_dict
            
        ret_dict = parse_data(rest_api_call_results, results_doc_definition, ret_dict)
        return ret_dict

if __name__ == "__main__":
    #wormbase_ids = ["WBGene00006763","WBGene00006764","WBGene00006765"]
    wormbase_ids = ["WBGene00006763"]
    wormbaseAPI = WormbaseAPI()
    for wormbase_id in wormbase_ids:
        call_type = "field"
        call_class = "gene"
        data_request = 'references'
        #data_request = 'overview'
        #data_request = 'gene_ontology'
        method_params = {}
        method_params['object_id']=wormbase_id
        method_params['data_request']=data_request
        method_params['call_type']=call_type
        method_params['call_class']=call_class
        ret_data = wormbaseAPI.get_wormbase_data(method_params)

        pretty_data = json.dumps(ret_data, indent=4)
        print(pretty_data)
        with open('result.json', 'w') as file:
                file.write(pretty_data)
    #df = pd.json_normalize(pretty_data['gene_ontology_summary'])
    #df.to_csv('output.csv', index=False)