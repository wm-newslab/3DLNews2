import os
import gzip
import json
import hashlib
import requests
from urllib.parse import urlparse
from NwalaTextUtils.textutils import parallelGetTxtFrmURIs
from tqdm import tqdm

# Define paths
preprocessed_dir = "preprocessed_state"  # Path where preprocessed data is stored
html_dir_base = "HTML"  # Directory to store downloaded HTML files

def getURIHash(uri):
    """Generate MD5 hash for a given URI."""
    return hashlib.md5(uri.encode()).hexdigest()

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

def process_preprocessed_file(input_file_path, state_code, year):
    """
    Process a single preprocessed JSONL file and fill missing fields:
    - Fetch HTML, extract title, response code, expanded URL.
    - Save HTML content to a local file.
    - Write updated JSON object back to output file.
    """
    
    # Define output file name
    output_file_path = input_file_path.replace('preprocessed_', 'updated_preprocessed_')
    
    # Create the directory for the output file if it does not exist
    output_dir = os.path.dirname(output_file_path)  # Extract directory from output file path
    create_directory(output_dir)  # Ensure the output directory exists
    
    print(f"Processing file: {input_file_path}")
    
    # Open the preprocessed JSONL file for reading and create an output file for writing
    with gzip.open(input_file_path, 'rt', encoding='utf-8') as infile, gzip.open(output_file_path, 'wt', encoding='utf-8') as outfile:
        for line in tqdm(infile, desc=f"Processing links in {os.path.basename(input_file_path)}"):
            json_obj = json.loads(line.strip())
            link = json_obj.get('link')

            if link:
                print(f"Processing link: {link}")
                try:
                    # Fetch HTML content and metadata from the link
                    doc_lst = parallelGetTxtFrmURIs([link], cleanHTML=False, addResponseHeader=True)
                except requests.exceptions.ConnectionError:
                    print(f"Connection error occurred while accessing {link}. Skipping.")
                    doc_lst = None
                except Exception as e:
                    print(f"An error occurred while processing {link}: {e}")
                    doc_lst = None

                # If doc_lst is not None and contains valid response history
                if doc_lst and 'info' in doc_lst[0] and 'response_history' in doc_lst[0]['info']:
                    response_history = doc_lst[0]['info']['response_history']

                    # Extract expanded URL if there are multiple redirects
                    if len(response_history) > 1:
                        expanded_url = response_history[-1]['url']
                        print(f"Expanded URL: {expanded_url}")
                    else:
                        expanded_url = None
                    
                    # Extract title from the fetched document
                    title = doc_lst[0].get('title', None)
                    if title:
                        print(f"Extracted title: {title}")
                    
                    # Extract response code
                    response_code = response_history[-1]['status_code']
                    print(f"Response code: {response_code}")

                    # Save HTML to file if response is valid (200 OK)
                    if response_code == 200:
                        html_dir = f'{html_dir_base}/{state_code}/{year}'
                        create_directory(html_dir)  # Ensure the directory exists
                        html_filename = f'{html_dir}/{getURIHash(link)}.html.gz'
                        
                        # Save HTML content to file
                        with gzip.open(html_filename, 'wt', encoding='utf-8') as html_file:
                            html_file.write(doc_lst[0]['text'])
                        print(f"HTML content saved to: {html_filename}")
                    else:
                        html_filename = None
                        print(f"Failed to fetch valid HTML for link: {link}")
                else:
                    expanded_url = None
                    title = None
                    response_code = None
                    html_filename = None
                    print(f"Skipping link {link} due to errors or invalid response.")
                
                # Update the JSON object with the newly fetched data
                json_obj.update({
                    'title': title,
                    'response_code': response_code,
                    'expanded_url': expanded_url,
                    'html_filename': html_filename
                })

            # Write the updated JSON object back to the output file
            outfile.write(json.dumps(json_obj) + '\n')
        
        print(f"Finished processing file: {input_file_path}")
        print(f"Output written to: {output_file_path}")



def process_all_preprocessed_files():
    """Iterate through all preprocessed files and process them."""
    print(f"Starting processing of all preprocessed files in {preprocessed_dir}")
    
    # Iterate over each state directory inside the preprocessed directory
    for state_code in tqdm(os.listdir(preprocessed_dir), desc="Processing all states"):
        state_path = os.path.join(preprocessed_dir, state_code)
        if os.path.isdir(state_path):
            print(f"\nProcessing state directory: {state_code}")
            
            # Iterate over all files in the state directory
            for file_name in tqdm(os.listdir(state_path), desc=f"Processing files in {state_code}"):
                if file_name.endswith('.jsonl.gz') and file_name.startswith('preprocessed_'):
                    year = extract_year(file_name)
                    input_file_path = os.path.join(state_path, file_name)
                    print(f"Processing file: {input_file_path} for year: {year}")
                    process_preprocessed_file(input_file_path, state_code, year)
                    
    print("All preprocessed files have been processed.")

def extract_year(filename):
    """Extract the year from the filename using a regex pattern."""
    import re
    pattern = r'\d{4}'
    match = re.search(pattern, filename)
    if match:
        return match.group()
    else:
        return None

# Start processing all preprocessed files
if __name__ == "__main__":
    print("Starting the script to process preprocessed files...")
    process_all_preprocessed_files()
    print("Processing complete!")
