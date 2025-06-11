import os
import requests
import gzip
import shutil
import csv
import sys
import json
import re
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path

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



def annotation_files_list(wormbase_version):
    url = f"https://downloads.wormbase.org/releases/{wormbase_version}/species/c_elegans/PRJNA13758/annotation/"
    
    response = requests.get(url, timeout=10)
    
    # Check if the request was successful
    if response.status_code != 200:
        print(f"Failed to retrieve webpage. Status code: {response.status_code}")
        return []
    
    # Parse HTML content using Beautiful Soup
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find all table rows
    rows = soup.find_all('tr')
    
    # Initialize list to store file names
    file_names = []
    
    # Iterate over table rows
    for row in rows:
        # Find the second table data (td) element in the row
        td = row.find_all('td')
        
        # Check if the row has at least two td elements
        if len(td) > 1:
            file_name = td[1].find('a').text
            file_names.append(file_name)
    
    # Remove the first element (Parent Directory)
    file_names = file_names[1:]
    
    prefix = f"c_elegans.PRJNA13758.{wormbase_version}."
    file_names = [name.replace(prefix, "") for name in file_names]
    
    return file_names

   
def _download_url(file_url, output_file_path):
    response = requests.get(file_url, stream=True)
    if response.status_code == 200:
        with open(output_file_path, 'wb') as f:
            shutil.copyfileobj(response.raw, f)
        print(f"Downloaded: {output_file_path}")
    else:
        print(f"Failed to download: {file_url} (status code: {response.status_code})")
    return

def download_annotation_file(wormbase_version, file_nm, output_dir):
    annotation_nm = f"c_elegans.PRJNA13758.{wormbase_version}.{file_nm}"

    base_url = f"https://downloads.wormbase.org/releases/{wormbase_version}/species/c_elegans/PRJNA13758"
    file_url = f"{base_url}/annotation/{annotation_nm}"

    # Ensure output directory exists
    os.makedirs(output_dir, exist_ok=True)

    # Download the file
    output_file_path = os.path.join(output_dir, annotation_nm)
    _download_url(file_url, output_file_path)

    ext_nm = annotation_nm[-3:]
    if ext_nm == ".gz":
        # Unzip the file
        with gzip.open(output_file_path, 'rb') as f_in:
            with open(output_file_path.rstrip('.gz'), 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)

        # Remove the .gz file if it exists
        if os.path.exists(output_file_path):
            os.remove(output_file_path)
            
        print(f"Unzipped: {output_file_path}")
        return output_file_path[:-3]
    
def download_gene_ids(wormbase_version, output_dir):
        return download_annotation_file(wormbase_version, "geneIDs.txt.gz", output_dir)
    
        
def gene_ids_to_csv(wormbase_version, source_dir, status_live=True):
    gene_ids = f"c_elegans.PRJNA13758.{wormbase_version}.geneIDs.txt"
    input_file = f"{source_dir}/{gene_ids}"

    if not os.path.exists(input_file):
        print(f"File '{input_file}' does not exist.")
        return
    
    # Generate the output file name
    output_file = f"{input_file[:-3]}csv"

    # Load the input CSV file into a DataFrame
    gene_ids_df = pd.read_csv(input_file, header=None)
    if status_live:
        # Filter rows where the 5th column equals 'Live'
        gene_ids_df = gene_ids_df[gene_ids_df[4] == 'Live']
        gene_ids_df = gene_ids_df[[1, 2, 3, 5]]
        gene_ids_df.columns = ["Wormbase_Id", "Gene_name", "Sequence_id", "Gene_Type"]
    else:
        gene_ids_df = gene_ids_df[[1, 2, 3, 4, 5]]
        gene_ids_df.columns = ["Wormbase_Id", "Gene_name", "Sequence_id", "Status", "Gene_Type"]
        
    # Save the result to the output file
    gene_ids_df.to_csv(output_file, index=False)

    print(f"Processed file saved to: {output_file}")
    return output_file



def _clean_sequence_id(sequence_id):
    if '.' in sequence_id:
        base, isoform = sequence_id.rsplit('.', 1)
        if re.fullmatch(r'\d+[A-Z]', isoform):
            return f"{base}.{isoform[:-1]}"
    return None

def _lookup_wormbase_id(sequence_id, gene_ids_dict):
    sequence_id = sequence_id.upper()
    found = gene_ids_dict.get(sequence_id)
    if not found and sequence_id.startswith("PSEUDOGENE:"):
        sequence_id = sequence_id[11:]
        found = gene_ids_dict.get(sequence_id)
    if not found and _clean_sequence_id(sequence_id):
        sequence_id = _clean_sequence_id(sequence_id)
        found = gene_ids_dict.get(sequence_id)
    if not found and '.' in sequence_id:
        sequence_id = sequence_id[0:sequence_id.rindex('.')]
        found = gene_ids_dict.get(sequence_id)
    if not found and _clean_sequence_id(sequence_id):
        sequence_id = _clean_sequence_id(sequence_id)
        found = gene_ids_dict.get(sequence_id)
    if found:
        return found
    else:
        return None


def map_wormbase_ids(sequence_ids_file_path, *, column_name='ID', gene_ids_df=None, working_dir_path=None):
    # Ensure input path is Path object
    sequence_ids_file_path = Path(sequence_ids_file_path)

    # Load sequence ID file
    try:
        sequence_ids_df = pd.read_csv(sequence_ids_file_path)
    except Exception as e:
        print(f"Error reading file: {sequence_ids_file_path}\n{e}")
        sys.exit(1)    
    
    # Set default working directory
    if working_dir_path is None:
        working_dir_path = sequence_ids_file_path.parent
    else:
        working_dir_path = Path(working_dir_path)
    
    if column_name not in sequence_ids_df.columns:
        print(f"{column_name} column is required in the input CSV")
        sys.exit(1)
    
    if gene_ids_df is None:
        wormbase_version = current_wormbase_version()
        gene_ids_csv_file_nm = working_dir_path / f"c_elegans.PRJNA13758.{wormbase_version}.geneIDs.csv"
        if not gene_ids_csv_file_nm.exists():
            gene_ids_txt = download_gene_ids(wormbase_version, working_dir_path)            
            gene_ids_csv_file_nm = gene_ids_to_csv(wormbase_version, working_dir_path, status_live=False)
            print(f"Created {wormbase_version} version of wormbase csv")

            # Clean up .txt file
            txt_path = Path(gene_ids_txt)
            if txt_path.exists():
                txt_path.unlink()
                
        gene_ids_df = pd.read_csv(gene_ids_csv_file_nm).fillna('')

            
    gene_ids_dict = {}
    for _, row in gene_ids_df.iterrows():
        for key in ['Wormbase_Id', 'Gene_name', 'Sequence_id']:
            id_val = str(row[key]).upper()
            gene_ids_dict[id_val] = row.to_dict()
            
    found_ids = []
    not_found_ids = []

    for _, row in sequence_ids_df.iterrows():
        input_id = str(row[column_name])
        match = _lookup_wormbase_id(input_id, gene_ids_dict)
        if match:
            match['Initial_Alias'] = input_id
            found_ids.append(match)
        else:
            not_found_ids.append(input_id)
                        
    num_found = len(found_ids)
    num_not_found = len(not_found_ids)
    totals = num_found + num_not_found
    percent_found = num_found / totals * 100
    
    print(f"Found     {num_found:>6,} genes.")
    print(f"Not Found {num_not_found:>6,} genes.")
    print(f"Processed {totals:>6,} genes.  {percent_found:.2f}% matched.")

    if not_found_ids:
        not_found_ids = sorted(not_found_ids)
        df = pd.DataFrame(not_found_ids, columns=['ID'])
        output_path = working_dir_path / 'wormbase_ids_not_found.csv'
        df.to_csv(output_path, index=False)
        print(f"Not Found IDs saved at {output_path}")
    
    found_ids = sorted(found_ids, key=lambda d: d['Wormbase_Id'])
    df = pd.DataFrame(found_ids)
    output_path = working_dir_path / 'wormbase_ids_found.csv'
    df.to_csv(output_path, index=False)
    print(f"Found IDs saved at {output_path}")