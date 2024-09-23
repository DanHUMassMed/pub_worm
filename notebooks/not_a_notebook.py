"""
    This script retrieves genomic sequences for promoter regions of given WormBase IDs using the Ensembl API. 
    It:
        1. Reads a CSV file containing WormBase IDs, chromosome numbers, and genomic positions.
        2. Adjusts positions to extract 2000 bp promoter regions (upstream or downstream).
        3. Uses asyncio to fetch sequences from Ensembl API in parallel.
        4. Divides the input DataFrame into chunks and processes them concurrently using a ProcessPoolExecutor.
        5. Combines results and saves them to a new CSV file containing WormBase IDs and corresponding genomic sequences.
"""
import os
import sys
import pandas as pd
import asyncio
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

sys.path.append("/Users/dan/Code/Python/pub_worm")
from pub_worm.ensembl.ensembl_api import async_get_sequence_region, async_create_fasta

def get_promoter_region(start_pos, stop_pos):
    if start_pos > stop_pos:
        print("3 prime")
        return stop_pos + 1, stop_pos + 2001
    elif stop_pos > start_pos:
        # Return Start_Pos-2001, Start_Pos-1
        #print("5 prime")
        return start_pos - 2001, start_pos - 1
    else:
        # Handle the case where Start_Pos == Stop_Pos (optional)
        raise ValueError("Start_Pos and Stop_Pos are equal, cannot adjust positions.")


def run_async_get_sequence(promoter_start, promoter_stop, chromosome):
    return asyncio.run(async_get_sequence_region(promoter_start, promoter_stop, chromosome))

# Function to process a chunk of the DataFrame
def process_chunk(chunk):
    results = []
    process_id = os.getpid() 
    total_ids = len(chunk)
    for idx, row in enumerate(chunk.itertuples()):
        wormbase_id = row.Wormbase_Id
        chromosome = row.Chromosome
        start_pos = row.Start_Pos
        stop_pos = row.Stop_Pos
        
        promoter_start, promoter_stop = get_promoter_region(start_pos, stop_pos)
        sequence = run_async_get_sequence(promoter_start, promoter_stop, chromosome)
        if sequence:
            results.append((wormbase_id,sequence))
        else:
            print(f"NO genomic_sequence for {wormbase_id}")
    
        if (idx + 1) % 100 == 0 or (idx + 1) == total_ids:  # Also print for the final iteration
            print(f"Processed {idx + 1} Wormbase IDs from process {process_id}")
        
    return results

# Function to divide DataFrame into chunks of 5000 rows
def divide_into_chunks(df, chunk_size=5000):
    for i in range(0, len(df), chunk_size):
        yield df[i:i + chunk_size]



if __name__ == "__main__":
    #genomic_position_df = pd.read_csv("./output/genomic_position.csv")
    genomic_position_df = pd.read_csv("./output/try_again.csv")

    # Divide the DataFrame into chunks of 5000 rows
    chunks = list(divide_into_chunks(genomic_position_df, chunk_size=5000))

    # Create a process pool with 10 processes
    num_processes = min(10, multiprocessing.cpu_count())

    with ProcessPoolExecutor(max_workers=num_processes) as executor:
        # Run each chunk in parallel
        futures = [executor.submit(process_chunk, chunk) for chunk in chunks]

        # Gather the results
        results = []
        for future in futures:
            results.extend(future.result())

    df_results = pd.DataFrame(results, columns=['Wormbase_Id', 'Sequence'])
    df_results.to_csv('./output/genomic_sequences1.csv', index=False)