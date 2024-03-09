from pub_worm.wormbase.wormbase_api import WormbaseAPI
from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd
import json

if __name__ == "__main__":
    #wormbase_ids = ["WBGene00006763","WBGene00006764","WBGene00006765"]

    #wormbase_ids = ["WBGene00000914"]
    wormbase_ids = ["WBPaper00053600"]
    wormbase_references = WormbaseAPI("widget", "gene", "references")
    wormbase_references = WormbaseAPI("widget", "gene", "gene_ontology")
    #wormbase_references = WormbaseAPI("field", "gene", "references")
    wormbase_references = WormbaseAPI("field", "paper", "abstract")

    for wormbase_id in wormbase_ids:
        ret_data = wormbase_references.get_wormbase_data(wormbase_id)
        pretty_data = json.dumps(ret_data, indent=4)
        print(pretty_data)
        with open('result.json', 'w') as file:
                file.write(pretty_data)

        #refereneces_to_csv(ret_data['references_list'])
        #ontology_to_csv(ret_data['gene_ontology_summary'])
