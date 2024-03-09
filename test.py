def remove_empty_dicts(obj):
    if isinstance(obj, dict):
        return {k: remove_empty_dicts(v) for k, v in obj.items() if v and remove_empty_dicts(v)}
    elif isinstance(obj, list):
        return [remove_empty_dicts(v) for v in obj if v and remove_empty_dicts(v)]
    else:
        return obj

# Your JSON data
json_data = {
    "gene_ontology_summary": {
        "Molecular_function": [
            {
                "name": "DNA-binding transcription factor activity, RNA polymerase II-specific",
                "id": "GO:0000981"
            },
            {
                "name": "DNA-binding transcription factor activity",
                "id": "GO:0003700"
            }
        ],
        "Cellular_component": [
            {
                "name": "nucleus",
                "id": "GO:0005634"
            },
            {}
        ],
        "Biological_process": [
            {
                "name": "defense response to Gram-negative bacterium",
                "id": "GO:0050829"
            },
            {
                "name": "male mating behavior",
                "id": "GO:0060179"
            },
            [
                {
                    "name": "regulation of gene expression",
                    "id": "GO:0010468"
                },
                {}
            ],
            [
                {
                    "name": "positive regulation of transcription by RNA polymerase II",
                    "id": "GO:0045944"
                },
                {}
            ],
            {
                "name": "serotonin biosynthetic process",
                "id": "GO:0042427"
            }
        ]
    }
}

# Remove empty dictionaries
json_data={}
cleaned_json = remove_empty_dicts(json_data)
print(cleaned_json)
