'''
ORCID API https://pub.orcid.org/v3.0
'''
import os
import time
import urllib.parse
import logging
import logging.config
import pandas as pd
import json
import requests

try:
    logging.config.fileConfig('logging.config')
except Exception:
    pass

# Create a logger object
logger = logging.getLogger(__name__)

class OrcidAPI:

    def __init__(self):
        self.base_url_str = "https://pub.orcid.org/v3.0"
        self.max_retries = 3
        self.timeout = 20
        self.api_key = os.environ.get('ORCID_ACCESS_TOKEN', None)


    def _rest_api_call(self, params):
        api_result = None
        api_error = "No Error Set"

        if 'orcid_id' not in params:
             logger.error("'orcid_id' param required but not passed.")
             return api_result
             
        if self.api_key is None:
             logger.error("'ORCID_ACCESS_TOKEN' is required but not found in env.")
             return api_result

        url_str = f"{self.base_url_str}/{params['orcid_id']}"

        headers = {
            "Accept": "application/vnd.orcid+json",
            "Authorization type and Access token": f"Bearer {self.api_key}"
        }

        # Query String may be used in the future
        # query = '&'.join([f"{urllib.parse.quote(k, 'utf-8')}={urllib.parse.quote(v, 'utf-8')}" for k, v in params.items()])
        # url_str = f"{url_str}?{query}"
        logger.debug(url_str)

        #self.max_retries = 3
        retry = 0
        done = False

        def handle_error(error_msg):
            print(error_msg)
            logger.debug(error_msg)
            nonlocal done, retry, api_error
            retry +=1
            if retry >= self.max_retries:
                done = True
                api_error = error_msg

        while not done:
            try:
                response = requests.get(url_str, headers=headers, timeout=self.timeout)
                response.raise_for_status()  # Check for HTTP errors
                if response.status_code == 200:
                    done = True
                    api_result = response.json()
                elif response.status_code == 429:
                    handle_error(f"Request limiter hit. waiting 2 seconds [Retry: {retry + 1}] code: {response.status_code}")
                    time.sleep(2)
                else:
                    handle_error(f"Failed to retrieve data. | Retry- {retry +1} | Response code- {response.status_code}")

            except Exception as ex:
                aviod_logging_interpolation=f"Error while calling url_str {str(ex)}"
                logger.error(aviod_logging_interpolation)
                error_msg=f"Unexpected Error | Retry- {retry+1} | Response msg- {str(ex)}"
                if isinstance(ex, requests.exceptions.HTTPError):
                        error_msg = f"Check the format of the http request [Retry: {retry + 1}] code: {str(ex)}"
                elif isinstance(ex, requests.exceptions.ConnectionError):
                        error_msg = f"Connection Error [Retry: {retry + 1}] code: {str(ex)}"
                elif isinstance(ex, requests.exceptions.Timeout):
                        error_msg = f"Timeout Error [Retry: {retry + 1}] code: {str(ex)}"
                handle_error(error_msg)

        if api_result is None:
            api_result = {"rest_api_error":api_error}

        if logger.isEnabledFor(logging.DEBUG):
            pretty_data = json.dumps(api_result, indent=4)
            with open('http_response.json', 'w', encoding="utf-8") as file:
                file.write(pretty_data)
            logger.debug(pretty_data)

        return api_result
    
    def get_orcid_data(self, orcid_id, map_result_to=None):

        if orcid_id is None:
            raise Exception("orcid_id cannot be null!")
    
        params = {'orcid_id':orcid_id}
        rest_api_call_results = self._rest_api_call(params)
        if "rest_api_error" in rest_api_call_results:
            return rest_api_call_results
        
        if map_result_to is None:
            return rest_api_call_results

        # Future code can be used to map results by parsing the json return object
        # for not we just return the whole thing!
        return rest_api_call_results

