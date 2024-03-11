from pub_worm.wormbase.wormbase_api import WormbaseAPI
#from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd
import json


def ontology_to_dataframe(json_obj, file_name=None):
    rows = []
    row = []
    for category, cat_lst in json_obj.items():
        #print(f"{category=}")
        #print(f"{cat_lst=}")
        row = [category]
        if isinstance(cat_lst, dict):
            row.append(cat_lst['id'])
            row.append(cat_lst['name'])
            rows.append(row)
            row = [category]
        else:
            for cat_lst_item in cat_lst:
                #print(f"{cat_lst_item=}")
                row.append(cat_lst_item['id'])
                row.append(cat_lst_item['name'])
                rows.append(row)
                row = [category]

    df = pd.DataFrame(rows)
    df.columns=["Category","Name","Id"]
    if file_name:
        df.to_csv(file_name, index=False)
    return df


if __name__ == "__main__":

    wormbase_id = "WBGene00000914"
    #wormbase_id = ["WBPaper00053600"]
    #wormbase_api = WormbaseAPI("widget", "gene", "references")
    #wormbase_api = WormbaseAPI("widget", "gene", "gene_ontology")
    #wormbase_api = WormbaseAPI("field", "gene", "references")
    #wormbase_api = WormbaseAPI("field", "paper", "abstract")
    wormbase_api = WormbaseAPI("field", "gene", "gene_ontology_summary")

    ret_data = wormbase_api.get_wormbase_data(wormbase_id)
    pretty_data = json.dumps(ret_data, indent=4)
    with open('result.json', 'w') as file:
            file.write(pretty_data)

    #refereneces_to_csv(ret_data['references_list'])
    #print(ret_data['gene_ontology_summary'])
    df = ontology_to_dataframe(ret_data['gene_ontology_summary'])
    print(df.head())
    

