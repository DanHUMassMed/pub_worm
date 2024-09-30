import os
import requests
import gzip
import shutil
import csv
import json
import pandas as pd

# Get the most current Wormbase DB
def current_wormbase_version():
    api_url = f'http://rest.wormbase.org//rest/database/version'
    # Absolutley no error checking is done!!
    response = requests.get(api_url)
    json_data = json.loads(response.text)
    if  response.status_code == 200:
        return json_data['data']
    else:
        return {'error':'something is not right'}

   
def _download_url(file_url, output_file_path):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(output_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Downloaded: {output_file_path}")
    else:
        print(f"Failed to download: {file_url} (status code: {response.status_code})")
    return

    
def download_gene_ids(wormbase_version, output_dir):
    gene_ids = f"c_elegans.PRJNA13758.{wormbase_version}.geneIDs.txt.gz"

    base_url = f"https://downloads.wormbase.org/releases/{wormbase_version}/species/c_elegans/PRJNA13758"
    file_url = f"{base_url}/annotation/{gene_ids}"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download the file
    output_file_path = os.path.join(output_dir, gene_ids)
    _download_url(file_url, output_file_path)

    # Unzip the file
    with gzip.open(output_file_path, 'rb') as f_in:
        with open(output_file_path.rstrip('.gz'), 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)

    # Remove the .gz file if it exists
    if os.path.exists(output_file_path):
        os.remove(output_file_path)
        
    print(f"Unzipped: {output_file_path}")
        
def extract_live_gene_ids(wormbase_version, source_dir):
    gene_ids = f"c_elegans.PRJNA13758.{wormbase_version}.geneIDs.txt"
    input_file = f"{source_dir}/{gene_ids}"

    if not os.path.exists(input_file):
        print(f"File '{input_file}' does not exist.")
        return
    
    # Generate the output file name
    output_file = f"{input_file[:-3]}csv"

    # Load the input CSV file into a DataFrame
    df = pd.read_csv(input_file, header=None)

    # Filter rows where the 5th column equals 'Live'
    df_filtered = df[df[4] == 'Live']

    # Select the required columns (2nd, 3rd, 4th, and 6th)
    df_selected = df_filtered[[1, 2, 3, 5]]

    # Add the appropriate column headers
    df_selected.columns = ["Wormbase_Id", "Gene_name", "Sequence_id", "Gene_Type"]

    # Save the result to the output file
    df_selected.to_csv(output_file, index=False)

    print(f"Processed file saved to: {output_file}")

