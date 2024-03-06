import json

# def iterate_json(json_obj, parent_key=None):
#     if isinstance(json_obj, dict):
#         for key, value in json_obj.items():
#             if parent_key:
#                 current_key = f"{parent_key}.{key}"
#             else:
#                 current_key = key
#             if isinstance(value, (dict, list)):
#                 iterate_json(value, current_key)
#             else:
#                 print(f"Key: {current_key}, Value: {value}")
#     elif isinstance(json_obj, list):
#         for index, item in enumerate(json_obj):
#             if isinstance(item, (dict, list)):
#                 iterate_json(item, f"{parent_key}[{index}]")
#             else:
#                 print(f"Key: {parent_key}[{index}], Value: {item}")

def process_dict_item(dict_item):
    header = []
    row_data = []
    for index, key in enumerate(dict_item.keys()):
        # header_nm += key
        # if len(dict_item.keys())>1 and index<len(dict_item.keys()-1):
        #     header +="."
        value = dict_item[key]
        if isinstance(value, list):
            data = process_list_item(value)
        elif isinstance(value, dict):
            pass
        else:
            data = value

        header.append(key)
        row_data.append(data)

    return header, data

def process_list_item(items):
    ret_val = ""
    for index, item in enumerate(items):
        
        ret_val += item
        if len(items)>1 and index<len(items-1):
            ret_val +=" | "
    return ret_val


def flatten_json_list(json_obj):
    header= []
    data = []
    if isinstance(json_obj, list):
        for list_item in json_obj:
            #create row
            row_header= []
            row_data = []
            if isinstance(list_item, dict):
                header, data =process_dict_item(list_item)
            elif isinstance(list_item, list):
                header,data = process_list_item(list_item)



        

    
with open("result.json", 'r') as file:
    json_data = json.load(file)

{
    "references_list": [
        {
            "year": "2018",
            "journal": [
                "G3 (Bethesda)"
            ],
            "title": [
                "Systematic Functional Characterization of Human 21st Chromosome Orthologs in Caenorhabditis elegans."
            ],
            "author": [
                {
                    "name": "Nordquist SK"
                },
                {
                    "name": "Smith SR"
                },
                {
                    "name": "Pierce JT"
                }
            ]
        },
        {
            "year": "2003",
            "journal": [
                "Neuron"
            ],
            "title": [
                "Endophilin is required for synaptic vesicle endocytosis by localizing synaptojanin."
            ],
            "author": [
                {
                    "name": "Schuske KR"
                },
                {
                    "name": "Richmond JE"
                },
                {
                    "name": "Matthies DS"
                },
                {
                    "name": "Davis WS"
                },
                {
                    "name": "Runz S"
                },
                {
                    "name": "Rube DA"
                },
                {
                    "name": "Van der Bliek AM"
                },
                {
                    "name": "Jorgensen EM"
                }
            ]
        }
]
}


# Start the iteration
flatten_json_list(json_data["references_list"])
