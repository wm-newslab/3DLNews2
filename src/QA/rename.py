import os
import gzip
import shutil

def rename_and_fix_json_gz(parent_directory):
    """
    Renames .json.gz files and ensures the contained .json file also has the updated name.
    """
    for root, dirs, files in os.walk(parent_directory):
        for file_name in files:
            if file_name.startswith("updated_updated_updated_") and file_name.endswith(".jsonl.gz"):
                # Construct new compressed file name
                new_name = file_name.replace("updated_updated_updated_", "", 1)
                old_compressed_path = os.path.join(root, file_name)
                new_compressed_path = os.path.join(root, new_name)

                # Rename the .json.gz file
                os.rename(old_compressed_path, new_compressed_path)
                print(f"Renamed: {old_compressed_path} -> {new_compressed_path}")

                # Decompress and rename the internal .json file
                temp_decompressed_path = new_compressed_path.replace(".jsonl.gz", ".jsonl")
                with gzip.open(new_compressed_path, 'rb') as compressed_file:
                    with open(temp_decompressed_path, 'wb') as decompressed_file:
                        shutil.copyfileobj(compressed_file, decompressed_file)

                # Rename the decompressed .json file
                old_internal_name = file_name.replace("updated_updated_updated_", "").replace(".gz", "")
                if os.path.exists(temp_decompressed_path):
                    new_internal_name = new_name.replace(".gz", "")
                    internal_file_path = os.path.join(root, old_internal_name)
                    new_internal_path = os.path.join(root, new_internal_name)
                    os.rename(temp_decompressed_path, new_internal_path)
                    print(f"Internal file renamed: {temp_decompressed_path} -> {new_internal_path}")

                    # Recompress the file with the updated name
                    with open(new_internal_path, 'rb') as internal_file:
                        with gzip.open(new_compressed_path, 'wb') as compressed_file:
                            shutil.copyfileobj(internal_file, compressed_file)

                    # Clean up the temporary uncompressed file
                    os.remove(new_internal_path)
                    print(f"Removed temporary file: {new_internal_path}")

# Specify the parent directory path
parent_directory_path = "preprocessed_state"
rename_and_fix_json_gz(parent_directory_path)

