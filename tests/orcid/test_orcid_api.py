import pytest
import json
import inspect
import os
from pub_worm.orcid.orcid_api import OrcidAPI

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

def test_get_orcid_data_from_orcid_id():
    function_name = inspect.currentframe().f_code.co_name
    orcid_id = "0000-0002-2403-8551"
    orcid_api = OrcidAPI()
    actual_result = orcid_api.get_orcid_data(orcid_id)
    dump_api_call(function_name, actual_result)
    
    expected_result = "Higgins"
    assert actual_result['person']['name']['family-name']['value'] == expected_result

if __name__ == "__main__":
    pytest.main([__file__])
