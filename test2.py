import json
import os 
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor
from pub_worm.ncbi.entreze_api import EntrezAPI
def check_issn_essn(json_data):
    if "issn" in json_data:
        return json_data["issn"]
    elif "essn" in json_data:
        return json_data["essn"]
    else:
        return None

def get_issn_essn(pmid):
    search_params = {'term':f"{pmid}[UID]"}
    summary_ret_data = EntrezAPI.get_ncbi_data(search_params, "paper_summary")
    if summary_ret_data:
        summary_ret_data['pmid']=pmid
        
    issn_essn = check_issn_essn(summary_ret_data)
    if issn_essn:
        imapact_factor = get_impact_factor(issn_essn)
        summary_ret_data['impact_factor']=imapact_factor
    return summary_ret_data
   

os.environ['NCBI_API_KEY'] = '5a1e23e51e6bf572435b326f1452a339ce08'

pmids = ["17875205","10854422","35143646","15837805","12610523","17889653","15943973","21647448","18028414","23091037"]
summary_ret_data_lst = []
for pmid in pmids:
    summary_ret_data = get_issn_essn(pmid)
    summary_ret_data_lst.append(summary_ret_data)
print(len(summary_ret_data_lst))
for summary_ret_data in summary_ret_data_lst:
    print(summary_ret_data)


