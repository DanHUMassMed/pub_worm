import json
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor
from pub_worm.ncbi.entreze_api import EntrezAPI
def check_issn_essn(json_data):
    if "issn" in json_data:
        return json_data["issn"]
    elif "essn" in json_data:
        return json_data["essn"]
    else:
        return None

search_params = {'term':"16291722[UID]"}
summary_ret_data = EntrezAPI.get_ncbi_data(search_params, "paper_summary")
issn_essn = check_issn_essn(summary_ret_data)
if issn_essn:
    imapact_factor = get_impact_factor(issn_essn)
    print(f"{imapact_factor=}")

pretty_data = json.dumps(summary_ret_data, indent=4)
print(pretty_data)

