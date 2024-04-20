import pytest
import json
import inspect
import os
from pub_worm.wormbase.wormbase_api import WormbaseAPI

DUMP_API_CALL = True
def dump_api_call(function_name, actual_result):
    if DUMP_API_CALL:
        pretty_data = json.dumps(actual_result, indent=4)
        output_path = "output"
        if not os.path.exists(output_path):
            os.makedirs(output_path)
        with open(f"{output_path}/{function_name}.json", 'w') as file:
                file.write(pretty_data)
        print(pretty_data)

def test_from_class_gene_request_gene_ontology_data():
    function_name = inspect.currentframe().f_code.co_name
    wormbase_id = "WBGene00195248"
    wormbase_api = WormbaseAPI("field", "gene", "gene_ontology_summary")
    actual_result = wormbase_api.get_wormbase_data(wormbase_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "GO:0022890"
    assert actual_result['gene_ontology_summary']['Molecular_function']['go_id'] == expected_result

def test_from_class_gene_request_references():
    function_name = inspect.currentframe().f_code.co_name
    wormbase_id = "WBGene00008205"
    #wormbase_id = "WBGene00195248"
    wormbase_api = WormbaseAPI("field", "gene", "references")
    actual_result = wormbase_api.get_wormbase_data(wormbase_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "WBPaper00043057"
    assert actual_result['references_list'][0]['wbp_id'] == expected_result

def test_from_class_gene_request_overview():
    function_name = inspect.currentframe().f_code.co_name
    wormbase_id = "WBGene00008205"
    #wormbase_id = "WBGene00195248"
    wormbase_api = WormbaseAPI("widget", "gene", "overview")
    actual_result = wormbase_api.get_wormbase_data(wormbase_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "sams-1"
    assert actual_result['wb_gene_name'] == expected_result

def test_from_class_paper_request_pmid():
    function_name = inspect.currentframe().f_code.co_name
    wormbase_paper_id = "WBPaper00027772"
    wormbase_api = WormbaseAPI("field", "paper", "pmid")
    actual_result = wormbase_api.get_wormbase_data(wormbase_paper_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "16291722"
    assert actual_result['pm_id'] == expected_result

def test_from_class_paper_request_abstract():
    function_name = inspect.currentframe().f_code.co_name
    wormbase_paper_id = "WBPaper00027772"
    wormbase_api = WormbaseAPI("field", "paper", "abstract")
    actual_result = wormbase_api.get_wormbase_data(wormbase_paper_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "Nephronophthisis (NPH) is a cystic kidney disorder"
    assert actual_result['wbp_abstract'].startswith(expected_result)

if __name__ == "__main__":
    pytest.main([__file__])
