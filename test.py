# Read references.csv
# Use WBPaper00064006 ids
# Call WormbaseAPI and get pubmed_ids
# Write the results back to references.csv
from pub_worm.wormbase.wormbase_api import WormbaseAPI
from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd


def assign_pubmed_id(row):
    wormbase_api = WormbaseAPI()
    method_params = {}
    method_params['object_id']=row['id']
    method_params['data_request']='pmid'
    method_params['call_type']='field'
    method_params['call_class']='paper'
    pmid_json =  wormbase_api.get_wormbase_data(method_params)
    print(pmid_json)
    ret_val = 'NA'
    if 'pmid' in pmid_json:
        ret_val = pmid_json['pmid']
    return ret_val

df = pd.read_csv('references.csv')
print(df.head())
df['pmid'] = df.apply(assign_pubmed_id, axis=1)
df = df[['pmid','id','journal','year','title','author','abstract']]
df.to_csv('output.csv', index=False)

# wormbase_api = WormbaseAPI()
# ret_val = wormbase_api.get_wormbase_data({'object_id': 'WBPaper00064006', 'data_request': 'pmid', 'call_type': 'field', 'call_class': 'paper'})
# print(ret_val)