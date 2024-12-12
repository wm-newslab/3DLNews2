import os
import gzip
import json

# Define the base directories
dir1 = "preprocessed_state"
dir2 = "updated_preprocessed_state"
mismatch_log_file = "mismatched_files.txt"

# Function to count JSON objects in a .jsonl.gz file
def count_json_objects(file_path):
    print(f"Counting JSON objects in file: {file_path}")
    count = 0
    try:
        with gzip.open(file_path, 'rt', encoding='utf-8') as f:
            for line in f:
                try:
                    json.loads(line.strip())
                    count += 1
                except json.JSONDecodeError:
                    print(f"Invalid JSON found in file: {file_path}")
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
    print(f"Finished counting: {count} objects found in {file_path}")
    return count

# List to store mismatched file information
mismatched_files = []

# Walk through directory 1 and find corresponding files in directory 2
print("Starting directory traversal...")
for root, _, files in os.walk(dir1):
    for file in files:
        if file.endswith(".jsonl.gz"):
            # Construct the corresponding file name in dir2
            file_path1 = os.path.join(root, file)
            relative_path = os.path.relpath(file_path1, dir1)
            
            # Add the "updated_" prefix to the file name in dir2
            relative_path_parts = relative_path.split(os.sep)
            relative_path_parts[-1] = "updated_" + relative_path_parts[-1]
            file_path2 = os.path.join(dir2, *relative_path_parts)

            print(f"Processing pair: \n  Original: {file_path1} \n  Updated: {file_path2}\n")

            # Check if the file exists in dir2
            if os.path.exists(file_path2):
                print(f"File found in updated directory: {file_path2}\n")
                count1 = count_json_objects(file_path1)
                count2 = count_json_objects(file_path2)

                if count1 != count2:
                    print(f"*** MISMATCH ***\n  {file_path1} ({count1} objects)\n  {file_path2} ({count2} objects)\n")
                    mismatched_files.append(f"{file_path1} ({count1} objects) vs {file_path2} ({count2} objects)")
                else:
                    print(f"Counts match for: \n  {file_path1} and {file_path2}\n")
            else:
                print(f"*** FILE NOT FOUND *** in updated directory: {file_path2}\n")
                mismatched_files.append(f"{file_path1} (file exists) vs {file_path2} (not found)")
print("Finished processing all files.")

# Save mismatches to a text file
print(f"Saving mismatches to {mismatch_log_file}...")
with open(mismatch_log_file, 'w') as log_file:
    log_file.write("Mismatched Files:\n")
    log_file.write("\n".join(mismatched_files))

# Print mismatches in the command line
if mismatched_files:
    print("\nMismatched Files:")
    for mismatch in mismatched_files:
        print(mismatch)
else:
    print("\nNo mismatched files found.")

