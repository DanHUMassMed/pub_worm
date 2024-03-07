'''
NCBI REST API for https://eutils.ncbi.nlm.nih.gov/entrez/eutils
'''
import time
import json
import urllib.request
import urllib.parse
import logging
import logging.config

logging.config.fileConfig('logging.config')
# Create a logger object
logger = logging.getLogger(__name__)

class EntrezAPI:

    def __init__(self):
        self.base_url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.max_retries = 3
        

    def rest_api_call(self, function_call, params):
        url_str = f"{self.base_url_str}/{function_call}.fcgi"
        params['retmode']='json'
        query = '&'.join([f"{urllib.parse.quote(k, 'utf-8')}={urllib.parse.quote(v, 'utf-8')}" for k, v in params.items()])
        url_str = f"{url_str}?{query}"
        logger.debug(url_str)

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
                        error_msg=f"Check the format of the http request [Retry: {retry + 1}] code: {str(ex)}"
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

    def get_ncbi_data(self, method_params):
        api_params = {}

        api_params['db']  = method_params['db']
        api_params['term']= method_params['term']
        function_call = method_params['function']
              
        get_json = self.get_json_element
    
        rest_api_call_results = self.rest_api_call(function_call, api_params)
        if "rest_api_error" in rest_api_call_results:
            return rest_api_call_results

        ret_dict = {}
        # wormbase_api_json = load_wormbase_api_json(call_type, call_class)
        # if data_request not in wormbase_api_json:
        #     logger.error(f"No wormbase connfig for {data_request=}")
        #     return {}
        # results_doc_definition = wormbase_api_json[data_request]

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
            results_dict = self.extract_skip_elements(results_dict)
            results_dict = self.extract_single_element_lists(results_dict)
            return results_dict
            
        #ret_dict = parse_data(rest_api_call_results, results_doc_definition, ret_dict)
        return ret_dict
