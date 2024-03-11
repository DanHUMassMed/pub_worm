from pub_worm.wormbase.wormbase_api import WormbaseAPI
#from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd
import json

if __name__ == "__main__":


    paper_ids = ['WBPaper00027772', 'WBPaper00046396', 'WBPaper00014661', 'WBPaper00024960', 'WBPaper00061202', 'WBPaper00024444', 'WBPaper00035071', 'WBPaper00028470', 'WBPaper00003509', 'WBPaper00053550', 'WBPaper00051560', 'WBPaper00038491', 'WBPaper00027309', 'WBPaper00015132', 'WBPaper00025249', 'WBPaper00064108', 'WBPaper00032252']

    wormbase_id = "WBPaper00027772"
    #wormbase_id = ["WBPaper00053600"]
    #wormbase_api = WormbaseAPI("widget", "gene", "references")
    #wormbase_api = WormbaseAPI("widget", "gene", "gene_ontology")
    #wormbase_api = WormbaseAPI("field", "gene", "references")
    #wormbase_api = WormbaseAPI("field", "paper", "abstract")
    #wormbase_api = WormbaseAPI("field", "gene", "gene_ontology_summary")
    wormbase_api = WormbaseAPI("field", "paper", "pmid")

    ret_data = wormbase_api.get_wormbase_data(wormbase_id)
    pretty_data = json.dumps(ret_data, indent=4)
    with open('result.json', 'w') as file:
            file.write(pretty_data)
    print(pretty_data)
    #refereneces_to_csv(ret_data['references_list'])
    #print(ret_data['gene_ontology_summary'])
    #df = ontology_to_dataframe(ret_data['gene_ontology_summary'])
    #print(df.head())
    

