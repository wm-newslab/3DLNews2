import os
import re

def find_missing_years(directory):
    # Define the range of years we are checking for
    expected_years = set(range(2010, 2025))

    # Pattern to extract the year from filenames
    file_pattern = re.compile(r"tv_articles_[A-Z]{2}_(\d{4})\.jsonl\.gz")

    # Traverse each state directory within the main directory
    for state_dir in os.listdir(directory):
        state_path = os.path.join(directory, state_dir)

        # Check if it's a directory (state folder)
        if os.path.isdir(state_path):

            # Set to keep track of years found in the filenames for the state
            available_years = set()

            # Process each file in the state directory
            for file in os.listdir(state_path):
                match = file_pattern.match(file)
                if match:
                    year = int(match.group(1))
                    available_years.add(year)

            # Calculate missing years for the state
            missing_years = sorted(expected_years - available_years)
            print(f"{state_dir}: {' '.join(map(str, missing_years))}")

# Specify the path to the main directory containing state directories
directory_path = "state"
find_missing_years(directory_path)

