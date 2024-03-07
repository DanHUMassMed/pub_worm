import json
import pandas as pd

def ontology_to_csv(json_obj,file_name='ontology.csv'):
    rows = []
    row = []
    for key1, value1 in json_obj.items():
        row = [key1]
        for list_value in value1:
            for key2, value2 in list_value.items():
                row.append(value2)
            rows.append(row)
            row = [key1]

    df = pd.DataFrame(rows)
    df.columns=["Category","Name","Id"]
    df.to_csv(file_name, index=False)
    return rows

def refereneces_to_csv(json_obj,file_name='references.csv'):
    df = pd.DataFrame(json_obj)
    #df.columns=["Category","Name","Id"]
    df.to_csv(file_name, index=False)

