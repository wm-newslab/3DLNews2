import os
import gzip
import json
from tqdm import tqdm
from urllib.parse import urlparse, unquote, urlsplit
import requests
import re
import pandas as pd
from htmldate import find_date
from concurrent.futures import ThreadPoolExecutor, TimeoutError

# Define paths
preprocessed_dir = "updated_updated_preprocessed_state_with_nc"  # Path where preprocessed data is stored
updated_preprocessed_dir = "updated_preprocessed_state_with_pd"  # Path to save files with updated is_news_article

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

def is_news_article(link, expanded_url, website):
    is_news_article = False
    if expanded_url:
        link = expanded_url

    if not is_valid_url(link):
       print(f"Invalid URL: {link}")
       return False
    
    print(f"\n ----\n {link} \n")
    parsed_url = urlparse(link)
    path_segments = [segment for segment in parsed_url.path.split('/') if segment]
    print(path_segments)
    domain = extract_domain(link)
    website_domain = extract_domain(website)
    expanded_website_domain = extract_domain(resolve_shortened_url(website))
    # if domain not in website_domain and (domain not in expanded_website_domain or expanded_website_domain not in domain):
    #     is_news_article = False
    #     print(f"The domain {domain} is not same as website domain: {expanded_website_domain}")
    if not path_segments:
        is_news_article = False
    else:
        depth = len(path_segments)
        print(depth)
        if depth >= 3:
            is_news_article = True
        elif depth <= 2 and any(has_special_characters(segment) for segment in path_segments[:2]):
            is_news_article = True
        else:
            is_news_article = False
    print(f"News website: {is_news_article} \n ----\n")
    return is_news_article

# Resolve all URIs to their final target URI
def resolve_shortened_url(url):
   try:
       response = requests.head(url, allow_redirects=True, timeout=5)
       if response.status_code == 200:
           return response.url
       elif response.status_code in [301, 302, 303, 307, 308]:
           # If it's a redirection, recursively resolve the redirected URL
           return resolve_shortened_url(response.headers['Location'])
       else:
           return url  # URL did not resolve to HTTP 200
   except (requests.RequestException, KeyError):
       return url  # Error occurred while the request or redirection handling
          
def has_special_characters(path_segment):
    return any(char in path_segment for char in "-_.")
    
def extract_domain(url):
    # Decode any URL-encoded characters
    decoded_url = unquote(url)
    
    # Parse the URL
    parsed_url = urlparse(decoded_url)
    
    # Get the netloc (domain) part
    domain = parsed_url.netloc
    
    # If the domain is empty, return None
    if not domain:
        return None
    
    # Clean the domain by removing any unwanted characters
    # Remove query parameters by splitting on '&' or '?'
    clean_domain = domain.split('&')[0]  # Remove query string starting with '&'
    clean_domain = clean_domain.split('?')[0]  # Remove query string starting with '?'

    # Remove 'www.' prefix if it exists
    if clean_domain.startswith("www."):
        clean_domain = clean_domain[4:]  # Strip 'www.'

    return clean_domain
    
def is_valid_url(url):
   # Validate if the URL follows the correct structure
   try:
       result = urlsplit(url)
       return all([result.scheme, result.netloc])
   except ValueError:
       return False

def extract_date_from_URL(url):
    date_match = re.findall(r'/(\d{4})[-/](\d{2})[-/](\d{2})/', url)
    if date_match:
        year, month, day = date_match[0]
        article_publish_date = f"{year}-{month}-{day}"
        return article_publish_date
    else:
        return None

def find_date_with_timeout(url, timeout=10):
    # Use ThreadPoolExecutor to execute the find_date function with a timeout
    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(find_date, url)
        try:
            publish_date = future.result(timeout=timeout)  # Wait for the result with the specified timeout
            return publish_date
        except TimeoutError:
            print(f"Timeout occurred while processing: {url}")
            return None
        except Exception as e:
            print(f"An error occurred while processing {url}: {e}")
            return None
    
def find_pub_date(url):
    pub_date = None
    try:
        publish_date = find_date_with_timeout(url)
        if publish_date:
            print(f"Publication date found: {publish_date} for {url}")
            pub_date = str(publish_date)
        else:
            publish_date = extract_date_from_URL(url)
            pub_date = str(publish_date)
            print(f"Extracted date from URL: {url} for {publish_date}")
    except Exception as e:
        publish_date = extract_date_from_URL(url)
        print(f"Error while finding date for {url}: {e}")
        pub_date = str(publish_date)
    return pub_date

def process_preprocessed_file(input_file_path):
    """
    Update only the 'is_news_article' field in each JSONL object from a preprocessed file.
    Save the updated data to a new output file.
    """
    # Define output file path
    output_file_path = input_file_path.replace(preprocessed_dir, updated_preprocessed_dir).replace('preprocessed_', 'updated_preprocessed_')
    
    # Check if the output file already exists to skip processing if it's already done
    if os.path.exists(output_file_path):
        print(f"Output file {output_file_path} already exists. Skipping processing for {input_file_path}.")
        return  # Skip further processing if the file already exists

    # Ensure output directory exists
    output_dir = os.path.dirname(output_file_path)
    create_directory(output_dir)
    
    print(f"Processing file: {input_file_path}")
    
    with gzip.open(input_file_path, 'rt', encoding='utf-8') as infile, gzip.open(output_file_path, 'wt', encoding='utf-8') as outfile:
        for line in tqdm(infile, desc=f"Updating 'publication_date' in {os.path.basename(input_file_path)}"):
            json_obj = json.loads(line.strip())
            link = json_obj.get('link')
            pub_date = find_pub_date(link)
            print(f"pub_date: {pub_date}")
            json_obj['publication_date'] 
            
            # Write the updated JSON object back to the output file
            outfile.write(json.dumps(json_obj) + '\n')
        
    print(f"Finished processing file: {input_file_path} \n ")

def process_all_preprocessed_files():
    """Iterate through all preprocessed files and update 'publication_date'."""
    print(f"Starting update of 'publication_date' for all preprocessed files in {preprocessed_dir}")
    
    # Process each state directory inside the preprocessed directory
    for state_code in tqdm(os.listdir(preprocessed_dir), desc="Processing all states"):
        state_path = os.path.join(preprocessed_dir, state_code)
        if os.path.isdir(state_path):
            print(f"\nProcessing state directory: {state_code}")
            
            # Process each file in the state directory
            for file_name in tqdm(os.listdir(state_path), desc=f"Processing files in {state_code}"):
                if file_name.endswith('.jsonl.gz') and file_name.startswith('updated_updated_preprocessed_'):
                    input_file_path = os.path.join(state_path, file_name)
                    process_preprocessed_file(input_file_path)
                    
    print("All files have been updated with 'publication_date'.")

# Run the processing function
if __name__ == "__main__":
    print("Starting the script to update 'publication_date'...")
    process_all_preprocessed_files()
    print("Update complete!")

