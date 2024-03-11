'''
NCBI REST API for https://eutils.ncbi.nlm.nih.gov/entrez/eutils
'''
import time
import json
import urllib.request
import urllib.parse
import logging
import logging.config
import re
import os
from . import load_ncbi_api_json

try:
    logging.config.fileConfig('logging.config')
except Exception:
    logging.basicConfig(level=logging.INFO)  # Example default logging configuration

# Create a logger object
logger = logging.getLogger(__name__)

class EntrezAPI:

    def __init__(self,function):
        self.base_url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
        self.max_retries = 3
        self.function = function
        self.ncbi_api_json = load_ncbi_api_json(function)
        self.api_key = os.environ.get('NCBI_API_KEY', None)
        # if function not in self.ncbi_api_json:
        #     logger.error(f"No NCBI connfig for {function=}")
        #     self.results_doc_definition = {}
        # else:
        #     self.results_doc_definition = self.ncbi_api_json[data_request]
        

    def rest_api_call(self, params):
        url_str = f"{self.base_url_str}/{self.function}.fcgi"
        params['retmode']='json'
        if self.api_key:
            params['api_key'] = self.api_key
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
                aviod_logging_interpolation=f"Error while calling url_str {str(ex)}"
                logger.error(aviod_logging_interpolation)
                error_msg=f"Check if you have a connection!! | Retry- {retry+1} | Response msg- {str(ex)}"
                if isinstance(ex, urllib.error.HTTPError):
                    if ex.code == 500:
                        error_msg = f"Check the format of the http request [Retry: {retry + 1}] code: {str(ex)}"
                    elif ex.code == 429:
                        error_msg = f"Request limiter hit. waiting 2 seconds [Retry: {retry + 1}] code: {str(ex)}"
                        time.sleep(2)
                handle_error(error_msg)

        if api_result is None:
            api_result = {"rest_api_error": api_error}
        
        if logger.isEnabledFor(logging.DEBUG):
            pretty_data = json.dumps(api_result, indent=4)
            with open('http_response.json', 'w') as file:
                file.write(pretty_data)
            #logger.debug(pretty_data)
                
        return api_result


    @staticmethod
    def get_ncbi_data(method_params, data_request):
            def replace_uid(uid, json_data):
                json_str = json.dumps(json_data)
                replaced_json_str = re.sub(r'\$UID', str(uid), json_str)
                replaced_json = json.loads(replaced_json_str)
                return replaced_json

            entrez_search_api = EntrezAPI('esearch')
            search_params = {}
            search_params['usehistory'] = 'y' 
            search_params['retmax']     = method_params.get('retmax', '200')
            search_params['restart']    = method_params.get('restart', '0')
            search_params['db']         = method_params.get('pubmed', 'pubmed')
            if "term" in method_params:
                search_params['term']   = method_params.get('term')

            else:
                logger.error("'term' is a required parameter but was not passed in!")
                return {}

            search_ret_data = entrez_search_api.rest_api_call(search_params)

            summary_params = {}
            summary_params['retmax']     = search_params.get('retmax', '200')
            summary_params['restart']    = search_params.get('restart', '0')
            summary_params['db']         = search_params.get('pubmed', 'pubmed')

            if 'esearchresult' in search_ret_data:
                esearchresult = search_ret_data['esearchresult']
                summary_params['query_key'] = esearchresult.get('querykey')
                summary_params['WebEnv']    = esearchresult.get('webenv')
            else:
                logger.error("'esearchresult' is expected in the return but was not found!")
                return {}

            entrez_summary_api = EntrezAPI('esummary')
            summary_ret_data = entrez_summary_api.rest_api_call(summary_params)
            ret_dict = {}

            ncbi_api_json = load_ncbi_api_json('esummary')
            results_doc_definition = ncbi_api_json[data_request]
            uid = search_params['term'][:-5]
            results_doc_definition = replace_uid(uid, results_doc_definition)
            ret_dict = EntrezAPI.parse_data(summary_ret_data, results_doc_definition, ret_dict)
            return ret_dict


    @staticmethod
    def get_json_element(json_data, path):
        result = json_data
        try:
            for key in path:
                result = result[key]
        except Exception: #KeyError TypeError
            result = None
        return result

    @staticmethod
    def extract_empty_dict(json_obj):
        if isinstance(json_obj, dict):
            return {k: EntrezAPI.extract_empty_dict(v) for k, v in json_obj.items() if v and EntrezAPI.extract_empty_dict(v)}
        elif isinstance(json_obj, list):
            return [EntrezAPI.extract_empty_dict(v) for v in json_obj if v and EntrezAPI.extract_empty_dict(v)]
        else:
            return json_obj
    
    @staticmethod
    def extract_single_element_lists(json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                json_obj[key] = EntrezAPI.extract_single_element_lists(value)
        elif isinstance(json_obj, list):
            # If list length is 1 remove list
            if len(json_obj) == 1:
                return EntrezAPI.extract_single_element_lists(json_obj[0])
            else:
                return [EntrezAPI.extract_single_element_lists(item) for item in json_obj]
        return json_obj

    @staticmethod
    def extract_skip_elements(json_obj):
        if isinstance(json_obj, dict):
            for key, value in json_obj.items():
                if key == "SKIP":
                    json_obj = EntrezAPI.extract_skip_elements(value)
                else:
                    json_obj[key] = EntrezAPI.extract_skip_elements(value)
        elif isinstance(json_obj, list):
            return [EntrezAPI.extract_skip_elements(item) for item in json_obj]
        return json_obj

    @staticmethod
    def parse_data(data_to_process, doc_definition, results_dict):    
        # data_request_item_nm="description" data_request_item=["fields", "concise_description","data","text"]
        # data_request_item_nm="author"      data_request_item={ "ROOT": ["author"], "CONCAT": ["label"] }
        for data_request_item_nm, data_request_item in doc_definition.items():
            logger.debug(f"{data_request_item_nm=}{data_request_item=}")
            if isinstance(data_request_item, list):
                data_request_item_path = data_request_item
                widget_item = EntrezAPI.get_json_element(data_to_process, data_request_item_path)
                if widget_item is not None:
                    results_dict[data_request_item_nm] = widget_item
            elif isinstance(data_request_item, dict):
                #logger.debug(f"BEFORE {data_request_item=}, {data_request_item['ROOT']=}")
                #pretty_data = json.dumps(data_to_process, indent=4)
                #logger.debug(f"BEFORE {pretty_data}")
                sub_data_to_process = EntrezAPI.get_json_element(data_to_process, data_request_item["ROOT"])
                if sub_data_to_process is None:
                    logger.debug(f"AFTER WTF")

                if sub_data_to_process is not None:
                    #pretty_data = json.dumps(sub_data_to_process, indent=4)
                    #logger.debug(f"AFTER {pretty_data}")
                    if "CONCAT" in data_request_item:
                        sub_results_str = ""
                        for sub_data_item in sub_data_to_process:
                            sub_results = EntrezAPI.parse_data(sub_data_item, data_request_item, {})
                            if "CONCAT" in sub_results:
                                sub_results_str +=str(f"{sub_results['CONCAT']}|")
                        results_dict[data_request_item_nm] = sub_results_str[:-1]
                        logger.debug(f"Found CONCAT")
                    else:
                        logger.debug(f"AFTER NO CONCAT")
                        if isinstance(sub_data_to_process, dict):
                            logger.debug(f"DICT {sub_data_to_process=}")
                            logger.debug(f"DICT {data_request_item=}")
                            results_dict[data_request_item_nm] = EntrezAPI.parse_data(sub_data_to_process, data_request_item, {})
                        else: #It is a list
                            sub_results_list = []
                            for sub_data_item in sub_data_to_process:
                                list_item_to_append = EntrezAPI.parse_data(sub_data_item, data_request_item, {})
                                logger.debug(f"LIST ITEM {list_item_to_append=}")
                                sub_results_list.append(list_item_to_append)
                            results_dict[data_request_item_nm] = sub_results_list

            else:
                logger.debug("!!"*40)

        # Post processing
        results_dict = EntrezAPI.extract_empty_dict(results_dict)
        results_dict = EntrezAPI.extract_skip_elements(results_dict)
        results_dict = EntrezAPI.extract_single_element_lists(results_dict)
        return results_dict
            