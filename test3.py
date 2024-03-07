from pub_worm.wormbase.wormbase_api import WormbaseAPI
from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd
import json

if __name__ == "__main__":
    #wormbase_ids = ["WBGene00006763","WBGene00006764","WBGene00006765"]
    wormbase_ids = ["WBGene00000914"]
    #wormbase_ids = ["WBPaper00053600"]
    wormbaseAPI = WormbaseAPI()
    for wormbase_id in wormbase_ids:
        call_type = "field"
        #call_type = "widget"
        call_class = "gene"
        #call_class = "paper"
        #data_request = "pmid"
        data_request = 'references'
        #data_request = 'overview'
        #data_request = 'gene_ontology'
        #data_request = "phenotype"
        method_params = {}
        method_params['object_id']=wormbase_id
        method_params['data_request']=data_request
        method_params['call_type']=call_type
        method_params['call_class']=call_class
        ret_data = wormbaseAPI.get_wormbase_data(method_params)

        pretty_data = json.dumps(ret_data, indent=4)
        print(pretty_data)
        with open('result.json', 'w') as file:
                file.write(pretty_data)

        refereneces_to_csv(ret_data['references_list'])
        #ontology_to_csv(ret_data['gene_ontology_summary'])
