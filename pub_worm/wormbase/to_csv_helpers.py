import json
import pandas as pd

def ontology_to_dataframe(json_obj, file_name=None):
    rows = []
    row = []
    for category, cat_lst in json_obj.items():
        print(f"{category=}")
        print(f"{cat_lst=}")
        row = [category]
        if isinstance(cat_lst, dict):
            row.append(cat_lst['id'])
            row.append(cat_lst['name'])
            rows.append(row)
            row = [category]
        else:
            for cat_lst_item in cat_lst:
                print(f"{cat_lst_item=}")
                row.append(cat_lst_item['id'])
                row.append(cat_lst_item['name'])
                rows.append(row)
                row = [category]

    df = pd.DataFrame(rows)
    df.columns=["Category","Name","Id"]
    if file_name:
        df.to_csv(file_name, index=False)
    return df


def refereneces_to_dataframe(json_obj, file_name=None):
    df = pd.DataFrame(json_obj)
    #df.columns=["Category","Name","Id"]
    if file_name:
        df.to_csv(file_name, index=False)
    return df

