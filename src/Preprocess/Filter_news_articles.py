import os
import gzip
import json
from tqdm import tqdm

preprocessed_dir = "preprocessed_state"  # Path where preprocessed data is stored
updated_preprocessed_dir = "filterd_data"  # Path to save filtered news article data

def create_directory(directory_path):
    """Create a directory if it doesn't exist."""
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")

def process_preprocessed_file(input_file_path):
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
        for line in tqdm(infile, desc=f"Filtering {os.path.basename(input_file_path)}"):
            json_obj = json.loads(line.strip())
            is_news_article = json_obj.get('is_news_article')
            if is_news_article:
                outfile.write(json.dumps(json_obj) + '\n')
    print(f"Finished filtering: {input_file_path} \n ")

def process_all_preprocessed_files():
    """Iterate through all preprocessed files and update 'publication_date'."""
    print(f"Collecting filtered data in {preprocessed_dir}")
    
    # Process each state directory inside the preprocessed directory
    for state_code in tqdm(os.listdir(preprocessed_dir), desc="Filtering all states"):
        state_path = os.path.join(preprocessed_dir, state_code)
        if os.path.isdir(state_path):
            print(f"\Filtering state directory: {state_code}")
            
            # Process each file in the state directory
            for file_name in tqdm(os.listdir(state_path), desc=f"Processing files in {state_code}"):
                if file_name.endswith('.jsonl.gz') and file_name.startswith('preprocessed_'):
                    input_file_path = os.path.join(state_path, file_name)
                    process_preprocessed_file(input_file_path)
    print("All files have been filtered.")

if __name__ == "__main__":
    print("Starting the script to filter news articles")
    process_all_preprocessed_files()
    print("Update complete!")
