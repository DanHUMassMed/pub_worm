import re
import json

def replace_uid(uid, json_data):
    json_str = json.dumps(json_data)
    replaced_json_str = re.sub(r'\$UID', str(uid), json_str)
    replaced_json = json.loads(replaced_json_str)
    return replaced_json

# Example usage
json_data = {
  "paper_summary": {
    "paper_summary": { 
        "source"     : ["result","$UID","source"],
        "lastauthor" : ["result","$UID","lastauthor"],
        "issn"       : ["result","$UID","issn"],
        "essn"       : ["result","$UID","essn"]        
    }
  }
}

replaced_json = replace_uid(111111, json_data)
print(replaced_json)

