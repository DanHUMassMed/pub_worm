'''
WormbaseREST REST API for http://rest.wormbase.org/index.html
'''
import time
import json
import urllib.request
import logging
import logging.config
from . import load_wormbase_api_json

try:
    logging.config.fileConfig('logging.config')
except Exception:
    logging.basicConfig(level=logging.INFO)  # Example default logging configuration

# Create a logger object
logger = logging.getLogger(__name__)

class WormbaseAPI:

    def __init__(self,call_type, call_class, data_request):
        self.base_url_str = "https://wormbase.org/rest"
        self.max_retries = 3
        self.call_type = call_type
        self.call_class = call_class
        self.data_request = data_request
        self.wormbase_api_json = load_wormbase_api_json(call_type, call_class)
        if data_request not in self.wormbase_api_json:
            logger.error(f"No wormbase connfig for {data_request=}")
            self.results_doc_definition = {}
        else:
            self.results_doc_definition = self.wormbase_api_json[data_request]
        

    def rest_api_call(self, object_id):
        url_str = f"{self.base_url_str}/{self.call_type}/{self.call_class}/{object_id}/{self.data_request}"
        retry = 0
        done = False

        api_result = None
        api_error = None

        def handle_error(error_msg):
            print(error_msg)
            nonlocal done, retry, api_error
            retry +=1
            if retry >= self.max_retries:
                done = True
                api_error = error_msg

        while not done:
            try:
                url = urllib.request.urlopen(url_str)
                if url.getcode() == 200:
                    done = True
                    response_text = url.read().decode('utf-8')
                    api_result = json.loads(response_text)
                elif url.getcode() == 429:
                    handle_error(f"Request limiter hit. waiting 2 seconds [Retry: {retry + 1}] code: {url.getcode()}")
                    time.sleep(2)
                else:
                    handle_error(f"Failed to retrieve data. | Retry- {retry +1} | Response code- {url.getcode()}")
            except Exception as ex:
                if isinstance(ex, urllib.error.HTTPError):
                    if ex.code == 500:
                        error_msg=f"Check the format of the http request [Retry: {retry + 1}]\nurl:{url_str}\ncode: {str(ex)}"
                else:
                    error_msg=f"Check if you have a connection!! | Retry- {retry+1} | Response msg- {str(ex)}"
                handle_error(error_msg)

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


    def extract_empty_dict(self, json_obj):
        if isinstance(json_obj, dict):
            return {k: self.extract_empty_dict(v) for k, v in json_obj.items() if v and self.extract_empty_dict(v)}
        elif isinstance(json_obj, list):
            return [self.extract_empty_dict(v) for v in json_obj if v and self.extract_empty_dict(v)]
        else:
            return json_obj
    
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

    def extract_skip_elements(self, json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == "SKIP":
                    json_obj = self.extract_skip_elements(value)
                else:
                    json_obj[key] = self.extract_skip_elements(value)
        elif isinstance(json_obj, list):
            return [self.extract_skip_elements(item) for item in json_obj]
        return json_obj

    def get_wormbase_data(self, object_id, map_result=True):
        # Just used to shorten the call length to make code more readable
        get_json = self.get_json_element

        if object_id is None:
            raise Exception("objectID cannot be null!")
    
        rest_api_call_results = self.rest_api_call(object_id)
        if "rest_api_error" in rest_api_call_results:
            return rest_api_call_results
        
        if not map_result:
            return rest_api_call_results

        ret_dict = {}

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
                    #logger.debug(f"BEFORE {data_request_item=}, {data_request_item['ROOT']=}")
                    #pretty_data = json.dumps(data_to_process, indent=4)
                    #logger.debug(f"BEFORE {pretty_data}")
                    sub_data_to_process = get_json(data_to_process, data_request_item["ROOT"])
                    if sub_data_to_process is None:
                        logger.debug(f"AFTER WTF")

                    if sub_data_to_process is not None:
                        #pretty_data = json.dumps(sub_data_to_process, indent=4)
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
                                    list_item_to_append = parse_data(sub_data_item, data_request_item, {})
                                    logger.debug(f"LIST ITEM {list_item_to_append=}")
                                    sub_results_list.append(list_item_to_append)
                                results_dict[data_request_item_nm] = sub_results_list

                else:
                    logger.debug("!!"*40)

            # Post processing
            results_dict = self.extract_empty_dict(results_dict)
            results_dict = self.extract_skip_elements(results_dict)
            results_dict = self.extract_single_element_lists(results_dict)
            return results_dict
            
        ret_dict = parse_data(rest_api_call_results, self.results_doc_definition, ret_dict)
        return ret_dict
