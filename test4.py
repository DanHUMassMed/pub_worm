from pub_worm.wormbase.wormbase_api import WormbaseAPI
from pub_worm.wormbase.to_csv_helpers import ontology_to_csv, refereneces_to_csv
import pandas as pd
import json
import time
import datetime
import psutil

# Function to monitor memory usage
def print_memory_usage():
    cpu_percent=psutil.cpu_percent()
    memory_percent=psutil.virtual_memory().percent
    memory_available=psutil.virtual_memory().available / (1024 ** 3)
    print(f"CPU {cpu_percent}% Memory {memory_percent}% Mem Avail {memory_available:,.2f} GB")

def get_abstracts(paper_ids, file_nm):
    formatted_date = datetime.date.today().strftime('%Y_%m_%d')
    file_name = f"{file_nm.lower().replace(' ', '_')}_references_{formatted_date}.csv"
    wormbase_abstract = WormbaseAPI("field", "paper", "abstract")
    concatenated_df = pd.DataFrame()
    dfs = []
    index=0
    number_of_rows=len(paper_ids)
    for  paper_id in paper_ids:
        print(f"{index:>4} of {number_of_rows} {paper_id}")
        #print(".", end='')
        index +=1
        #print(f"{index:<4} of {len(transmembrane_transport_df)} {row['wormbase_id']}")
        abstract_data = wormbase_abstract.get_wormbase_data(paper_id)
        if abstract_data:
                abstract_data_dict ={'paper_id':paper_id}
                abstract_data_dict.update(abstract_data)
                abstract_data_df = pd.DataFrame(abstract_data_dict, index=[0])
                dfs.append(abstract_data_df)
        else:
            print("-", end='')
            #print(f"Return has no references_list!\n{ret_data}")

        # Concatenate every 100 DataFrames
        # If something crashes we may be able to recover without a full rerun
        if index % 100 == 0:
            print(f"{index:>4} of {number_of_rows} {paper_id}")
            concatenated_df = pd.concat([concatenated_df] + dfs, ignore_index=True)
            concatenated_df.to_csv(file_name, index=False)
            print_memory_usage()
            dfs = []  # Reset the list for the next batch

    # Concatenate the remaining DataFrames
    if dfs:
        concatenated_df = pd.concat([concatenated_df] + dfs, ignore_index=True)
        concatenated_df.to_csv(file_name, index=False)
        print_memory_usage()
    return concatenated_df



if __name__ == "__main__":
    #wormbase_ids = ["WBGene00006763","WBGene00006764","WBGene00006765"]
    wormbase_ids = ["WBPaper00060138","WBPaper00037777","WBPaper00039838","WBPaper00055090","WBPaper00023603","WBPaper00017584","WBPaper00054980","WBPaper00038269","WBPaper00041771","WBPaper00031066","WBPaper00036096","WBPaper00028430","WBPaper00063976","WBPaper00032254","WBPaper00061065","WBPaper00034662","WBPaper00065135","WBPaper00031066","WBPaper00064863","WBPaper00065693","WBPaper00038444","WBPaper00031066","WBPaper00032254","WBPaper00050293","WBPaper00048924","WBPaper00042668","WBPaper00039571","WBPaper00031066","WBPaper00038491","WBPaper00042147","WBPaper00031066","WBPaper00055090","WBPaper00032254","WBPaper00038491","WBPaper00031066","WBPaper00055090","WBPaper00032254","WBPaper00031066","WBPaper00031066","WBPaper00032254","WBPaper00031066","WBPaper00032254","WBPaper00034662","WBPaper00065805","WBPaper00031066","WBPaper00028000"]
    #wormbase_ids = ["WBGene00000914"]
    #wormbase_ids = ["WBPaper00053600"]
    wormbase_references = WormbaseAPI("widget", "gene", "references")
    wormbase_references = WormbaseAPI("widget", "gene", "gene_ontology")
    #wormbase_references = WormbaseAPI("field", "gene", "references")
    wormbase_references = WormbaseAPI("field", "paper", "abstract")


    concatenated_df = get_abstracts(wormbase_ids, "abstract")
    print(f"Size {len(concatenated_df)}")
        
