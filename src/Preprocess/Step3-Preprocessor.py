import os
import gzip
import json
from tqdm import tqdm
from urllib.parse import urlparse, unquote, urlsplit
import requests

# Define paths
preprocessed_dir = "updated_preprocessed_state"  # Path where preprocessed data is stored
updated_preprocessed_dir = "updated_preprocessed_state_with_nc"  # Path to save files with updated is_news_article

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

def process_preprocessed_file(input_file_path):
    """
    Update only the 'is_news_article' field in each JSONL object from a preprocessed file.
    Save the updated data to a new output file.
    """
    # Define output file path
    output_file_path = input_file_path.replace(preprocessed_dir, updated_preprocessed_dir).replace('preprocessed_', 'updated_preprocessed_')
    
    # Ensure output directory exists
    output_dir = os.path.dirname(output_file_path)
    create_directory(output_dir)
    
    print(f"Processing file: {input_file_path}")
    
    with gzip.open(input_file_path, 'rt', encoding='utf-8') as infile, gzip.open(output_file_path, 'wt', encoding='utf-8') as outfile:
        for line in tqdm(infile, desc=f"Updating 'is_news_article' in {os.path.basename(input_file_path)}"):
            json_obj = json.loads(line.strip())
            link = json_obj.get('link')
            expanded_url = json_obj.get('expanded_url')
            website = json_obj.get('media-metadata', {}).get('website')
            
            # Determine if this is a news article
            is_article = is_news_article(link, expanded_url, website)
            json_obj['is_news_article'] = is_article
            
            # Write the updated JSON object back to the output file
            outfile.write(json.dumps(json_obj) + '\n')
        
    print(f"Finished processing file: {input_file_path} \n ")

def process_all_preprocessed_files():
    """Iterate through all preprocessed files and update 'is_news_article'."""
    print(f"Starting update of 'is_news_article' for all preprocessed files in {preprocessed_dir}")
    
    # Process each state directory inside the preprocessed directory
    for state_code in tqdm(os.listdir(preprocessed_dir), desc="Processing all states"):
        state_path = os.path.join(preprocessed_dir, state_code)
        if os.path.isdir(state_path):
            print(f"\nProcessing state directory: {state_code}")
            
            # Process each file in the state directory
            for file_name in tqdm(os.listdir(state_path), desc=f"Processing files in {state_code}"):
                if file_name.endswith('.jsonl.gz') and file_name.startswith('updated_preprocessed_'):
                    input_file_path = os.path.join(state_path, file_name)
                    process_preprocessed_file(input_file_path)
                    
    print("All files have been updated with 'is_news_article'.")

# Run the processing function
if __name__ == "__main__":
    print("Starting the script to update 'is_news_article'...")
    process_all_preprocessed_files()
    print("Update complete!")

