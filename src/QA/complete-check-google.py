import os
import gzip

def check_subdirectories(parent_dir):
    # Get all subdirectories in the parent directory
    subdirectories = [name for name in os.listdir(parent_dir) if os.path.isdir(os.path.join(parent_dir, name))]
    
    # List to store subdirectories that don't have exactly 30 `.jsonl.gz` files
    incomplete_dirs = []
    empty_files = []  # List to store names of truly empty `.jsonl.gz` files

    # Check each subdirectory
    for subdir in subdirectories:
        # Get the path of the subdirectory
        subdir_path = os.path.join(parent_dir, subdir)
        
        # List `.jsonl.gz` files in the subdirectory
        jsonl_gz_files = [file for file in os.listdir(subdir_path) if file.endswith('.jsonl.gz')]
        
        # Check if there are exactly 30 `.jsonl.gz` files
        if len(jsonl_gz_files) != 30:
            incomplete_dirs.append(subdir)

        # Check if any of the `.jsonl.gz` files are truly empty
        for file in jsonl_gz_files:
            file_path = os.path.join(subdir_path, file)
            try:
                # Open the file in read mode with gzip
                with gzip.open(file_path, 'rt') as f:
                    # Read the first chunk of data to check if the file is empty
                    if f.read(1) == '':  # If the first read returns an empty string, it's empty
                        empty_files.append((subdir, file))
            except Exception as e:
                print(f"Error reading {file_path}: {e}")

    # Print the names of subdirectories that don't have exactly 30 `.jsonl.gz` files
    if incomplete_dirs:
        print("Subdirectories without exactly 30 '.jsonl.gz' files:")
        for subdir in incomplete_dirs:
            print(subdir)
    else:
        print("All subdirectories contain exactly 30 '.jsonl.gz' files.")
    
    # Print the names of truly empty `.jsonl.gz` files, if any
    if empty_files:
        print("\nTruly empty '.jsonl.gz' files found:")
        for subdir, file in empty_files:
            print(f"Subdirectory: {subdir}, Empty file: {file} (Truly empty)")
    else:
        print("No truly empty '.jsonl.gz' files found.")

# Set your main directory path here
parent_directory_path = 'state'
check_subdirectories(parent_directory_path)

