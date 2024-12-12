import json
import gzip
import os

def extract_links(json_obj):
    return json_obj["links"]

parent_directory = "state"

output_file_path = "Twitter-Newspaper-Links.txt"

with open(output_file_path, 'w') as output_file:
    for subdir, _, files in os.walk(parent_directory):
        for file_name in files:
            if file_name.endswith(".jsonl.gz"):
                file_path = os.path.join(subdir, file_name)
                with gzip.open(file_path, 'rt', encoding='utf-8') as file:
                    for line in file:
                        json_obj = json.loads(line)
                        links = extract_links(json_obj)
                        for link in links:
                            output_file.write(link + '\n')


