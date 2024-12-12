import os
import gzip
import json

parent_dir = 'state'
output_file = 'Local_News_Article_Links-2-Twitter.txt'


# Function to extract links from a json object
def extract_links_from_jsonl_gz(file_path):
    links = []
    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
        for line in f:
            data = json.loads(line)
            for key, value in data.items():
                if 'links' in value:
                    for link in value['links']:
                        print(link['link'])
                        links.append(link['link'])
    return links


# Function to traverse directories and find all jsonl.gz files
def find_all_jsonl_gz_files(directory):
    jsonl_gz_files = []
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.jsonl.gz'):
                print(file)
                jsonl_gz_files.append(os.path.join(root, file))
    return jsonl_gz_files


# Extract all links from all jsonl.gz files
all_links = []
jsonl_gz_files = find_all_jsonl_gz_files(parent_dir)
for file_path in jsonl_gz_files:
    all_links.extend(extract_links_from_jsonl_gz(file_path))

# Save all links to the output file
with open(output_file, 'w') as f:
    for link in all_links:
        f.write(link + '\n')

print(f"Extracted {len(all_links)} links and saved to {output_file}")
