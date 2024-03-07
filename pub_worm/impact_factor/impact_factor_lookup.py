from pub_worm.impact_factor import impact_factor_df

def get_impact_factor(issn):
    # Look for ISSN or eISSN in the provided DataFrame
    match = impact_factor_df[(impact_factor_df['ISSN'] == issn) | (impact_factor_df['eISSN'] == issn)]
    if not match.empty:
        return match.iloc[0]['2021 JIF']
    else:
        return None