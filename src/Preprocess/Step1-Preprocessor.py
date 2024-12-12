import os
import re
import gzip
import json
import pandas as pd
import gzip
from htmldate import find_date
import signal
from NwalaTextUtils.textutils import parallelGetTxtFrmURIs
import hashlib
import requests
from urllib.parse import urlparse, unquote, urlsplit
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, TimeoutError
from htmldate import find_date

# Define paths
base_dir = "state"  # Path where state directories exist
preprocessed_dir = "preprocessed_state"  # Path where preprocessed data will be stored

# Create the preprocessed_state directory if not exists
os.makedirs(preprocessed_dir, exist_ok=True)

def is_valid_url(url):
   # Validate if the URL follows the correct structure
   try:
       result = urlsplit(url)
       return all([result.scheme, result.netloc])
   except ValueError:
       return False

# Function to map media details from the CSV based on website URL
def get_media_info(website, media_metadata_df):
    result = media_metadata_df[media_metadata_df['website'].str.contains(website, na=False)]
    if not result.empty:
        return {
            'media_name': result['media-name'].values[0],
            'state': result['state'].values[0],
            'city': result['city'].values[0],
            'longitude': result['city-county-long'].values[0],
            'latitude': result['city-county-lat'].values[0],
            'media-metadata': result['media-metadata'].values[0]
        }
    return None

def getURIHash(uri):
    return getStrHash(uri)

def getStrHash(txt):
    txt = txt.strip()
    if txt == '':
        return ''
    hash_object = hashlib.md5(txt.encode())
    return hash_object.hexdigest()

def extract_year(filename):
    pattern = r'\d{4}'
    match = re.search(pattern, filename)
    if match:
        return match.group()
    else:
        return None

def create_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

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
            print(f"Extracted date from URL: {publish_date} for {url}")
            pub_date = str(publish_date)
    except Exception as e:
        publish_date = extract_date_from_URL(url)
        print(f"Error while finding date for {url}: {e}")
        pub_date = str(publish_date)
    return pub_date

def is_special_domain(link):
    social_domains = ["facebook.com", "twitter.com", "youtube.com", "google.com"]
    parsed_url = urlparse(link)
    return any(domain in parsed_url.netloc for domain in social_domains)

def path_depth(link):
    parsed_url = urlparse(link)
    return len([segment for segment in parsed_url.path.split('/') if segment])

def has_special_characters(path_segment):
    return any(char in path_segment for char in "-_.")

from urllib.parse import urlparse, unquote

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

def is_news_article(link, expanded_url, website):
    is_news_article = False
    if expanded_url:
        link = expanded_url

    if not is_valid_url(link):
       print(f"Invalid URL: {link}")
       return False

    parsed_url = urlparse(link)
    path_segments = [segment for segment in parsed_url.path.split('/') if segment]

    domain = extract_domain(link)
    website_domain = extract_domain(website)
    if domain not in website_domain:
       expanded_website_domain = extract_domain(resolve_shortened_url(website))
       if domain not in expanded_website_domain or expanded_website_domain not in domain:
           is_news_article = False
           print(f"The domain {domain} is not same as website domain: {expanded_website_domain}")
    elif not path_segments:
        is_news_article = False
    else:
        depth = len(path_segments)
        if depth >= 3:
            is_news_article = True
        elif depth <= 2 and any(has_special_characters(segment) for segment in path_segments[:2]):
            is_news_article = True
        else:
            is_news_article = False

    return is_news_article

# Function to process each state directory and generate preprocessed JSONL files
def process_state_directory(state_code, media_metadata_df):
    state_dir = os.path.join(base_dir, state_code)
    output_dir = os.path.join(preprocessed_dir, state_code)
    os.makedirs(output_dir, exist_ok=True)

    print(f"Processing directory for state: {state_code}")
    
    for file_name in tqdm(os.listdir(state_dir), desc=f"Processing files in {state_code}"):
        if file_name.endswith('.jsonl.gz'):
            output_filename = f"preprocessed_{file_name}"
            input_file_path = os.path.join(state_dir, file_name)
            output_file_path = os.path.join(output_dir, output_filename)
            year = extract_year(file_name)
            
            # Check if the output file already exists
            if os.path.exists(output_file_path):
                print(f"Output file {output_file_path} already exists, skipping.")
                continue  # Skip this file if it already exists
            
            # Track links that are being written in this session
            written_links = set()

            with gzip.open(input_file_path, 'rt', encoding='utf-8') as infile, gzip.open(output_file_path, 'wt', encoding='utf-8') as outfile:
                for line in infile:
                    json_obj = json.loads(line.strip())
                    for website, details in json_obj.items():
                        media_info = get_media_info(website, media_metadata_df)
                        if media_info and 'links' in details:
                            for link_obj in details['links']:
                                link = link_obj.get('link')
                                if link and link != "#" and link != website and link not in written_links:
                                    url = link.strip()
                                    # try:
                                    #     doc_lst = parallelGetTxtFrmURIs([url], cleanHTML=False, addResponseHeader=True)
                                    # except requests.exceptions.ConnectionError:
                                    #     print(f"Connection error occurred while accessing {url}. Skipping.")
                                    #     doc_lst = None
                                    # except Exception as e:
                                    #     print(f"An error occurred: {e}")
                                    #     doc_lst = None

                                    # if doc_lst != None and len(doc_lst[0]['info']) != 0 and len(doc_lst[0]['info']['response_history']) > 1:
                                    #     expanded_url = doc_lst[0]['info']['response_history'][-1]['url']
                                    # else:
                                    #     expanded_url = None

                                    # if doc_lst != None and len(doc_lst[0]['info']) > 0:
                                    #     title = doc_lst[0]['title']
                                    # else:
                                    #     title = None

                                    # if doc_lst != None and len(doc_lst[0]['info']) != 0 and doc_lst[0]['info']['response_history'][-1]['status_code'] == 200:
                                    #     if year:
                                    #         html_dir = f'HTML/{state_dir}/{year}'
                                    #         create_directory(html_dir)
                                    #         html_filename = f'{html_dir}/{getURIHash(url)}.html.gz'
                                    #         with gzip.open(html_filename, 'wt', encoding='utf-8') as html_file:
                                    #             html_file.write(doc_lst[0]['text'])
                                    # else:
                                    #     html_filename = None

                                    # if doc_lst != None and len(doc_lst[0]['info']) != 0:
                                    #     response_code = doc_lst[0]['info']['response_history'][-1]['status_code']
                                    # else:
                                    #     response_code = None

                                    new_json_obj = {
                                        'link': url,
                                        'publication_date': None, #find_pub_date(url)
                                        'media_name': media_info['media_name'],
                                        'media_type': "radio",
                                        'location': {
                                            'state': media_info['state'],
                                            'city': media_info['city'],
                                            'longitude': media_info['longitude'],
                                            'latitude': media_info['latitude']
                                        },
                                        'media-metadata': json.loads(media_info["media-metadata"]),
                                        'source': "Google",
                                        'source_metadata': details,
                                        "title": None,  #title
                                        'response_code': None, #response_code
                                        'expanded_url': None, #expanded_url
                                        'html_filename': None, #html_filename
                                        'is_news_article': None #is_news_article(url, expanded_url, website)
                                    }
                                    outfile.write(json.dumps(new_json_obj) + '\n')

# Function to iterate over all state directories and process each
def process_all_states(media_metadata_df):
    # Check if the base directory exists
    if not os.path.exists(base_dir):
        print(f"The directory {base_dir} does not exist.")
        return
    
    # Iterate over each state directory inside the base directory
    for state_code in tqdm(os.listdir(base_dir), desc="Processing all states"):
        state_path = os.path.join(base_dir, state_code)
        if os.path.isdir(state_path):
            print(f"Processing state: {state_code}")
            process_state_directory(state_code, media_metadata_df)

# Load the CSV file to examine its structure
csv_file_path = 'media-metadata.csv'

# Read the CSV file into a DataFrame
media_metadata_df = pd.read_csv(csv_file_path)

# Display the first few rows of the dataframe to understand its structure
media_metadata_df.head()

# Start processing all states
process_all_states(media_metadata_df)
