import requests
import aiohttp
import asyncio
import aiofiles

def get_sequence_region(start_position, end_position, chromosome, species = "caenorhabditis_elegans"):
    sequence = ""
    try:
        # Construct the URL for the Ensembl API
        url = f"https://rest.ensembl.org/sequence/region/{species}/{chromosome}:{start_position}..{end_position}?content-type=text/plain"
        
        # Send the GET request
        response = requests.get(url, timeout=10)

        # Check if the request was successful
        if response.status_code == 200:
            sequence = response.text
        else:
            print(f"Failed to retrieve sequence. Status code: {response.status_code}")

    except requests.exceptions.Timeout:
        print("The request timed out. Please try again later.")
    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")
    return sequence


async def async_get_sequence_region(start_position, end_position, chromosome, species="caenorhabditis_elegans", max_retries=3):
    sequence = ""
    url = f"https://rest.ensembl.org/sequence/region/{species}/{chromosome}:{start_position}..{end_position}?content-type=text/plain"
    
    retries = 0

    while retries < max_retries:
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=10) as response:
                    # Check if the request was successful
                    if response.status == 200:
                        sequence = await response.text()
                        return sequence  # Return if successful
                    elif response.status_code == 429:
                        retry_after = response.headers.get('Retry-After')
                        if retry_after:
                            print(f"Rate limited. Retrying after {retry_after} seconds...")
                            asyncio.sleep(float(retry_after))  # Wait for the time specified by the server
                            retries += 1  # Increment retry count
                        else:
                            print("Rate limited. No Retry-After Waiting 2 seconds...")
                            asyncio.sleep(2)  # Wait for the time specified by the server
                            retries += 1  # Increment retry count
                            
                    else:
                        print(f"Failed to retrieve sequence. Status code: {response.status}")
                        retries += 1
                        await asyncio.sleep(2)  # Wait before retrying

        except Exception as e:
            print(f"An error occurred: {e} Retry {retries + 1}/{max_retries}.")
            retries += 1
            await asyncio.sleep(2)  # Wait before retrying

    print(f"Failed to retrieve sequence after {max_retries} attempts.")
    return sequence  # Return empty sequence if retries exhausted



def create_fasta(gene_nm, chromosome, sequence, path="."):
    # Define the filename based on the gene name
    filename = f"{path}/{gene_nm}.fasta"
    
    # Open the file in write mode
    with open(filename, 'w') as file:
        # Write the header line
        file.write(f">{chromosome}\n")
        
        # Write the sequence in lines of 60 characters
        for i in range(0, len(sequence), 60):
            file.write(sequence[i:i+60] + "\n")


async def async_create_fasta(gene_nm, chromosome, sequence, path="."):
    # Define the filename based on the gene name
    filename = f"{path}/{gene_nm}.fasta"
    
    # Open the file in asynchronous write mode
    async with aiofiles.open(filename, 'w') as file:
        # Write the header line
        await file.write(f">{chromosome}\n")
        
        # Write the sequence in lines of 60 characters
        for i in range(0, len(sequence), 60):
            await file.write(sequence[i:i+60] + "\n")
    
    