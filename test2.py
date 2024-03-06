import pandas as pd
import json

# JSON data
json_data = {
    "gene_ontology_summary": {
        "Molecular_function": [
            {
                "go_term": {
                    "name": "phosphatidylinositol-4,5-bisphosphate 5-phosphatase activity",
                    "id": "GO:0004439"
                }
            },
            {
                "go_term": {
                    "name": "phosphatase activity",
                    "id": "GO:0016791"
                }
            },
            {
                "go_term": {
                    "name": "hydrolase activity",
                    "id": "GO:0016787"
                }
            },
            {
                "go_term": {
                    "name": "phosphatidylinositol-3,5-bisphosphate 5-phosphatase activity",
                    "id": "GO:0043813"
                }
            }
        ],
        "Cellular_component": [
            {
                "go_term": {
                    "name": "synaptic vesicle",
                    "id": "GO:0008021"
                }
            },
            {
                "go_term": {
                    "name": "synapse",
                    "id": "GO:0045202"
                }
            },
            {
                "go_term": {
                    "name": "cytoplasmic vesicle",
                    "id": "GO:0031410"
                }
            }
        ],
        "Biological_process": [
            {
                "go_term": {
                    "name": "synaptic vesicle budding from presynaptic endocytic zone membrane",
                    "id": "GO:0016185"
                }
            },
            {
                "go_term": {
                    "name": "vesicle organization",
                    "id": "GO:0016050"
                }
            },
            {
                "go_term": {
                    "name": "synaptic vesicle transport",
                    "id": "GO:0048489"
                }
            },
            {
                "go_term": {
                    "name": "phosphatidylinositol-3-phosphate biosynthetic process",
                    "id": "GO:0036092"
                }
            },
            {
                "go_term": {
                    "name": "protein localization to synapse",
                    "id": "GO:0035418"
                }
            },
            {
                "go_term": {
                    "name": "locomotion",
                    "id": "GO:0040011"
                }
            },
            {
                "go_term": {
                    "name": "phosphatidylinositol dephosphorylation",
                    "id": "GO:0046856"
                }
            },
            {
                "go_term": {
                    "name": "acetylcholine transport",
                    "id": "GO:0015870"
                }
            },
            {
                "go_term": {
                    "name": "positive regulation of multicellular organism growth",
                    "id": "GO:0040018"
                }
            }
        ]
    }
}



def process_json(json_data):
    rows = []
    for key, value in json_data.items():
        if isinstance(value, list):
            for i, item in enumerate(value, start=1):
                if isinstance(item, dict):
                    row = [f"{key}"]
                    for k, v in item['go_term'].items():
                        row.append(v)
                    rows.append(row)
        elif isinstance(value, dict):
            for k, v in value.items():
                if isinstance(v, dict):
                    row = [f"{key}"]
                    for _, vv in v.items():
                        row.append(vv)
                    rows.append(row)
    return rows

def process_dict(dict, row=[], header=[], header_index=0):
    header_index=0
    for key, value in dict.items():
        if isinstance(value, list):
            process_list(key, value, row, header, header_index)
        elif isinstance(value, dict):
            process_dict(value, row, header, header_index)
        else:
            header.append(key)
            row.append(value)
    return row, header
        

def process_list(key, value, row, header, header_index):
    row = [f"{key}"]
    header = [f"list_{header_index}"]
    header_index = +1

    for lst_item in lst:
        if isinstance(lst_item, list):
            process_list(key,lst_item,  row, header, header_index)
        elif isinstance(lst_item, dict):
            process_dict(lst_item, row, header, header_index)
        else: #must be name value pair
            print("do not know how to handle list values")
            pass


def process_json2(json_data):
    rows = []
    header = []
    header_index=0
    if isinstance(json_data, list):
        row, header = process_list(json_data)
        rows.append()
    else:
        row, header = process_dict(json_data)
    return rows

rows = process_json2(json_data['gene_ontology_summary'])
for row in rows:
    print(row)
#df = pd.DataFrame(rows, columns=['name', 'id'])
#df.to_csv('output.csv', index=False)
