import os
import time
import requests
import urllib.parse
from bs4 import BeautifulSoup
import pandas as pd

import logging
import logging.config

try:
    logging.config.fileConfig('logging.config')
except Exception:
    logging.basicConfig(filename='pub_worm_entrez.log', level=logging.DEBUG)

# Create a logger object
logger = logging.getLogger(__name__)

def rest_api_call(function, params, data=None):
    base_url_str = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    url_str = f"{base_url_str}/{function}.fcgi"

    params['retmode']='xml'

    api_key = os.environ.get('NCBI_API_KEY', None)
    if api_key:
        params['api_key'] = api_key

    query = '&'.join([f"{urllib.parse.quote(k, 'utf-8')}={urllib.parse.quote(v, 'utf-8')}" for k, v in params.items()])
    url_str = f"{url_str}?{query}"
    logger.debug(url_str)

    # Data to be sent in the body of the request
      

    max_retries = 3
    retry = 0
    done = False

    api_result = None
    api_error = "No Error Set"

    def handle_error(error_msg):
        print(error_msg)
        logger.debug(error_msg)
        nonlocal done, retry, api_error
        retry +=1
        if retry >= max_retries:
            done = True
            api_error = error_msg

    while not done:
        try:
            if data:
                post_data = { "id": ",".join(data) } 
                response = requests.post(url_str, data=post_data)
            else:
                response = requests.get(url_str)
            response.raise_for_status()  # Check for HTTP errors
            if response.status_code == 200:
                done = True
                api_result = response.text
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
        api_result = f"<response><rest_api_error>{api_error}</rest_api_error></response>"
    
    if logger.isEnabledFor(logging.DEBUG):
        soup = BeautifulSoup(api_result, "xml")
        # Pretty-print the XML content
        pretty_data = soup.prettify()
        with open('http_response.xml', 'w') as file:
            file.write(pretty_data)
        #logger.debug(pretty_data)
            
    return api_result

def get_required_param(params, param_name, esummary_params):
    if param_name in params:
        esummary_params[param_name] = params[param_name]
    else:
        logger.debug(f"Param '{param_name}' is required but not passed")
        return False
    return True

def get_tag_text(doc, tag_name, attribute=None):
    if attribute:
        tag = doc.find(tag_name, attribute)
    else:
        tag = doc.find(tag_name)
    return tag.text if tag else ""


def entreze_epost(params, data):
    function="epost"
    epost_params = {}
    epost_params['db']  = params.get('db', 'pubmed')
    if data is None:
        logger.debug("Param 'data' is required but not passed.")

    api_result = rest_api_call(function, epost_params, data)
    ret_params = {}
    # Parse the XML response using BeautifulSoup
    soup = BeautifulSoup(api_result, "xml")
    # Extract WebEnv and QueryKey
    web_env   = get_tag_text(soup,"WebEnv")
    query_key = get_tag_text(soup,"QueryKey")
    api_error = get_tag_text(soup,"rest_api_error")
    ret_params['query_key'] = query_key
    ret_params['WebEnv']    = web_env
    if api_error:
        logger.error("Error in entreze_epost")
        ret_params = {}
        ret_params["Error"] = api_error

    return ret_params


def entreze_pmid_summaries(params):
    function="esummary"
    esummary_params = {}
    esummary_params['db']  = params.get('db', 'pubmed')

    required_params = ['query_key', 'WebEnv']
    for param_name in required_params:
        if not get_required_param(params, param_name, esummary_params):
            return []
 
    api_result = rest_api_call(function, esummary_params)
    # Parse the XML response using BeautifulSoup
    soup = BeautifulSoup(api_result, "xml")

    api_error = get_tag_text(soup,"rest_api_error")
    if api_error:
        logger.error("Error in entreze_pmid_summaries")
        # Maybe throw and exception here
        return []
        

    paper_summarys = []
    # Extract information for each UID
    for doc in soup.find_all("DocSum"):
        uid         = get_tag_text(doc, "Id")
        issn        = get_tag_text(doc, "Item", {"Name": "ISSN"})
        essn        = get_tag_text(doc, "Item", {"Name": "ESSN"})
        last_author = get_tag_text(doc, "Item", {"Name": "LastAuthor"})
        pmc_id      = get_tag_text(doc, "Item", {"Name": "pmc"})
        paper_summary = {
            "uid"         : uid,
            "issn"        : issn,
            "essn"        : essn,
            "last_author" : last_author,
            "pmc_id"      : pmc_id
        }
        paper_summarys.append(paper_summary)

    return paper_summarys


def entreze_pmid_fetch(params):
    function="efetch"
    efetch_params = {}
    efetch_params['db']  = params.get('db', 'pubmed')

    required_params = ['query_key', 'WebEnv']
    for param_name in required_params:
        if not get_required_param(params, param_name, efetch_params):
            return []
 
    api_result = rest_api_call(function, efetch_params)
    # Parse the XML response using BeautifulSoup
    soup = BeautifulSoup(api_result, "xml")

    api_error = get_tag_text(soup,"rest_api_error")
    if api_error:
        logger.error("Error in entreze_pmid_efetch")
        # Maybe throw and exception here
        return []
        

    # Pretty-print the XML content
    pretty_data = soup.prettify()
    with open('http_response1.xml', 'w') as file:
        file.write(pretty_data)

    paper_summarys = []
    # # Extract information for each UID
    # for doc in soup.find_all("DocSum"):
    #     uid         = get_tag_text(doc, "Id")
    #     issn        = get_tag_text(doc, "Item", {"Name": "ISSN"})
    #     essn        = get_tag_text(doc, "Item", {"Name": "ESSN"})
    #     last_author = get_tag_text(doc, "Item", {"Name": "LastAuthor"})
    #     pmc_id      = get_tag_text(doc, "Item", {"Name": "pmc"})
    #     paper_summary = {
    #         "uid"         : uid,
    #         "issn"        : issn,
    #         "essn"        : essn,
    #         "last_author" : last_author,
    #         "pmc_id"      : pmc_id
    #     }
    #     paper_summarys.append(paper_summary)

    return paper_summarys