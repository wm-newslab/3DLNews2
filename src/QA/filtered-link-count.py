import os
import gzip
import json

def count_json_objects(directory):
    total_count = 0  # Total JSON objects
    news_article_count = 0  # JSON objects with "is_news_article": true

    # Track the number of directories and files processed
    dir_count = 0
    file_count = 0

    # Traverse the directory
    for state_dir in os.listdir(directory):
        state_path = os.path.join(directory, state_dir)

        # Check if it's a directory (state folder)
        if os.path.isdir(state_path):
            dir_count += 1
            print(f"Processing directory: {state_dir} (#{dir_count})")

            for file in os.listdir(state_path):
                if file.endswith('.jsonl.gz'):
                    file_path = os.path.join(state_path, file)
                    file_count += 1
                    print(f"  Processing file: {file} (#{file_count}) in {state_dir}")

                    # Open and read the .jsonl.gz file
                    with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                        line_count = 0
                        for line in f:
                            line_count += 1
                            try:
                                json_obj = json.loads(line.strip())
                                total_count += 1
                                if json_obj.get("is_news_article") == True:
                                    news_article_count += 1
                            except json.JSONDecodeError:
                                print(f"    Skipping invalid JSON at line {line_count} in {file_path}")

                        print(f"    Finished processing {line_count} lines in {file}")

    print("Processing complete.")
    return total_count, news_article_count

# Specify the path to the main directory containing state directories
directory_path = "updated_updated_preprocessed_state_with_nc"
total, news_articles = count_json_objects(directory_path)

print(f"Total JSON objects: {total}")
print(f"JSON objects with 'is_news_article': true: {news_articles}")

