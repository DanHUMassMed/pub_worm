import pytest
import inspect
import os
import json
from bs4 import BeautifulSoup
from pub_worm.ncbi.entreze_api import EntrezAPI

DUMP_API_CALL = True
def dump_api_call(function_name, actual_result,data_type="json"):
    if DUMP_API_CALL:
        output_path = "output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)

        if data_type == 'json':
            pretty_data = json.dumps(actual_result, indent=4)
        elif data_type == 'json':
            soup = BeautifulSoup(actual_result, "xml")
            # Pretty-print the XML content
            pretty_data = soup.prettify()
        else:
            data_type=None

        if data_type:
            with open(f"{output_path}/{function_name}.{data_type}", 'w') as file:
                file.write(pretty_data)

        #with open("output.txt", "w") as file:
        #file.write(mystring)


def test_entreze_esearch():
    function_name = inspect.currentframe().f_code.co_name
    search_term = "Marnett L[au] AND (2019/01/01:2024/04/16[pdat])AND (vanderbilt[affil])"
    esearch_params = {'term': search_term }

    ncbi_api = EntrezAPI()
    actual_result = ncbi_api.entreze_esearch(esearch_params)
    dump_api_call(function_name, actual_result, "json")

    expected_result = "1"
    assert 'query_key' in actual_result, "'query_key' found in result"
    assert actual_result['query_key'] == expected_result


def test_entreze_epost():
    function_name = inspect.currentframe().f_code.co_name
    data = ["10021351", "10022905", "10022914", "10022975", "10048487", "10048958", "10049162", "10049362", "10049567", "10049576", "10051671", "10051850", "10064800", "10066248"]

    ncbi_api = EntrezAPI()
    actual_result = ncbi_api.entreze_epost(data)
    dump_api_call(function_name, actual_result, "json")

    expected_result = "1"
    assert 'query_key' in actual_result, "'query_key' found in result"
    assert actual_result['query_key'] == expected_result


def test_entreze_pmid_summaries():
    function_name = inspect.currentframe().f_code.co_name
    data = ["10021351"]

    ncbi_api = EntrezAPI()
    interm_result = ncbi_api.entreze_epost(data)

    actual_result = {}
    if 'WebEnv' in interm_result:
        actual_result = ncbi_api.entreze_pmid_summaries(interm_result)
        dump_api_call(function_name, actual_result, "json")


    assert len(actual_result) == 1, f"Expected exactly 1 result found but {len(actual_result)}"
    assert 'issn' in actual_result[0], "'issn' not found in result"
    assert actual_result[0]['issn'] == "0950-1991",f"Expected 'issn' to equal 0950-1991 but found {actual_result[0]['issn']}"

def test_entreze_epost_efetch():
    function_name = inspect.currentframe().f_code.co_name
    data = ["10021351"]

    ncbi_api = EntrezAPI()
    interm_result = ncbi_api.entreze_epost(data)

    actual_result = {}
    assert 'WebEnv' in interm_result, "Expected 'WebEnv' in interm_result"

    actual_result = ncbi_api.entreze_efetch(interm_result)
    dump_api_call(function_name, actual_result, "json")

    assert len(actual_result['articles']) == 1, f"Expected exactly 1 result found but {len(actual_result['articles'])}"
    assert 'pub_abbr' in actual_result['articles'][0], "'pub_abbr' not found in result"
    assert actual_result['articles'][0]['pub_abbr'] == "Development",f"Expected 'pub_abbr' to equal Development but found {actual_result['articles'][0]['pub_abbr']}"

def test_entreze_epost_efetch_full_article():
    function_name = inspect.currentframe().f_code.co_name
    data = ["PMC8253488","6358295"]
    params= {'db': 'pmc'}

    ncbi_api = EntrezAPI()
    interm_result = ncbi_api.entreze_epost(data, params)

    actual_result = {}
    assert 'WebEnv' in interm_result, "Expected 'WebEnv' in interm_result"

    actual_result = ncbi_api.entreze_efetch(interm_result)
    dump_api_call(function_name, actual_result, "json")

    #assert len(actual_result) == 1, f"Expected exactly 1 result found but {len(actual_result)}"
    #assert 'pub_abbr' in actual_result[0], "'pub_abbr' not found in result"
    #assert actual_result[0]['pub_abbr'] == "Development",f"Expected 'pub_abbr' to equal Development but found {actual_result[0]['pub_abbr']}"

def test_entreze_esearch_to_elink():
    function_name = inspect.currentframe().f_code.co_name
    search_term = "Marnett L[au] AND (2019/01/01:2024/04/16[pdat])AND (vanderbilt[affil])"
    esearch_params = {'term': search_term }

    ncbi_api = EntrezAPI()
    interm_result = ncbi_api.entreze_esearch(esearch_params)

    expected_result = "1"
    assert 'query_key' in interm_result, "'query_key' found in result"
    assert interm_result['query_key'] == expected_result

    actual_result = ncbi_api.entreze_elink_pmid_to_pmcid(interm_result)
    dump_api_call(function_name, actual_result, "json")

def test_entreze_esearch_efetch():
    function_name = inspect.currentframe().f_code.co_name
    
    search_term = "Marnett L[au] AND (2019/01/01:2024/04/16[pdat])AND (vanderbilt[affil])"
    esearch_params = {'term': search_term }

    ncbi_api = EntrezAPI()
    interm_result = ncbi_api.entreze_esearch(esearch_params)

    actual_result = {}
    assert 'WebEnv' in interm_result, "Expected 'WebEnv' in interm_result"

    actual_result = ncbi_api.entreze_efetch(interm_result)
    dump_api_call(function_name, actual_result, "json")

    # assert len(actual_result) == 1, f"Expected exactly 1 result found but {len(actual_result)}"
    # assert 'issn' in actual_result[0], "'issn' not found in result"
    # assert actual_result[0]['issn'] == "0950-1991",f"Expected 'issn' to equal 0950-1991 but found {actual_result[0]['issn']}"


if __name__ == "__main__":
    pytest.main([__file__])
