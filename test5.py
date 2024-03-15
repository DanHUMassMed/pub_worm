from pub_worm.impact_factor.impact_factor_lookup import get_impact_factor
from pub_worm.ncbi.entreze_post import entreze_epost, entreze_pmid_summaries
import pandas as pd
import json

if __name__ == "__main__":
    pmids = ["10021351", "10022905", "10022914", "10022975", "10048487", "10048958", "10049162", "10049362", "10049567", "10049576", "10051671", "10051850", "10064800", "10066248"]
    ret_data =entreze_epost({}, pmids) # pmids[:2]
    if 'WebEnv' in ret_data:
        ret_data = entreze_pmid_summaries(ret_data)
    print(ret_data)