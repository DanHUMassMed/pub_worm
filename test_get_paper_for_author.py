import json
import os 
from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor
from pub_worm.ncbi.entreze_api import EntrezAPI
from pub_worm.ncbi.entreze_post import entreze_pmid_fetch

os.environ['NCBI_API_KEY'] = '5a1e23e51e6bf572435b326f1452a339ce08'

def get_paper_for_author(query):
    search_params = {'term':query}
    summary_ret_data = EntrezAPI.get_ncbi_data(search_params, "paper_summary")    
    return summary_ret_data
   
if __name__ == "__main__":
    query = '"Serhna C"[au] OR Serhan CN[au] AND (2019/01/01:2024/04/16[pdat])'
    entrez_search_api = EntrezAPI('esearch')
    search_params = {}
    search_params['usehistory'] = 'y' 
    search_params['retmax']     = '200'
    search_params['restart']    = '0'
    search_params['db']         = 'pubmed'
    search_params['term']       = query
    search_ret_data = entrez_search_api.rest_api_call(search_params)
    if 'esearchresult' in search_ret_data:
        summary_params = {}
        summary_params['retmax']     = search_params.get('retmax', '200')
        summary_params['restart']    = search_params.get('restart', '0')
        summary_params['db']         = search_params.get('pubmed', 'pubmed')
        
        esearchresult = search_ret_data['esearchresult']
        summary_params['query_key'] = esearchresult.get('querykey')
        summary_params['WebEnv']    = esearchresult.get('webenv')

        summary_ret_data = entreze_pmid_fetch(summary_params)

        #entrez_summary_api = EntrezAPI('esummary')
        #summary_ret_data = entrez_summary_api.rest_api_call(summary_params)
        print(summary_ret_data)    
    else:
        print("'esearchresult' is expected in the return but was not found!")
    
    
    



