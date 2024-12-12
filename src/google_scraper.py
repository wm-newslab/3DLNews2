# From https://github.com/oduwsdl/scraper
from scraper.Google import googleSearch
from scraper.ScraperUtil import get_google_date_range_directive

import argparse
import json
import logging
import gzip
import time
import os

logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s', level=logging.DEBUG)

# Argument parsing
parser = argparse.ArgumentParser(description='Process some media types.')
parser.add_argument('media_type', type=str, choices=['newspaper', 'tv', 'radio', 'broadcast'], help='Type of media')
parser.add_argument('state_years', nargs='+', help='States and corresponding year periods in the format STATE:START_YEAR-END_YEAR (e.g., UT:2012-2020)')
parser.add_argument('sleep_sec', type=float, help='Seconds to sleep between requests')
parser.add_argument('media_file', type=str, help='Path to the media JSON gzip file')
parser.add_argument('max_pages', type=int, help='Max pages to scrape per query')

args = parser.parse_args()

media_type = args.media_type
state_years = args.state_years
sleep_sec = args.sleep_sec
media_file = args.media_file
max_pages = args.max_pages

# Parse the state-year arguments into a dictionary
state_year_ranges = {}
for state_year in state_years:
    state, years = state_year.split(':')
    start_year, end_year = map(int, years.split('-'))
    state_year_ranges[state] = (start_year, end_year)

# Start timer
overall_start_time = time.time()

# Function to create directory
def create_directory(directory_path):
    try:
        os.makedirs(directory_path, exist_ok=True)
        logging.info(f"Directory '{directory_path}' is ready.")
    except OSError as e:
        logging.error(f"Error creating directory '{directory_path}': {e}")

# Open and parse media file
try:
    with gzip.open(media_file, 'rt', encoding='utf-8') as file:
        data = json.load(file)
except (OSError, json.JSONDecodeError) as e:
    logging.error(f"Failed to open or parse media file {media_file}: {e}")
    exit(1)

# Path for execution time log
execution_times_file_path = f'{media_type.capitalize()}/execution_times.txt'
create_directory(f'{media_type.capitalize()}')

# Process the specified states
for state, (start_year, end_year) in state_year_ranges.items():
    if state not in data:
        logging.warning(f"State '{state}' not found in the media file. Skipping.")
        continue

    key_start_time = time.time()
    media_org = data[state]
    create_directory(f'{media_type.capitalize()}/{state}')

    # Process year by year
    for year in range(start_year, end_year + 1):
        start_date, end_date = f'{year}-01-01', f'{year}-12-31'
        date_range_directive = get_google_date_range_directive(start_date, end_date)
        serp_data = []

        # Process each media website for the current state
        for media_website in media_org:
            query = 'news'
            extraParams = {
                'directives': f'site:{media_website}',
                'search_query_params': date_range_directive,
                'no_interleave': False,
                'sleep_sec': sleep_sec
            }

            try:
                serp = googleSearch(query, maxPage=max_pages, extraParams=extraParams)
                serp_data.append({media_website: serp})
            except Exception as e:
                logging.error(f"Error fetching Google results for {media_website}: {e}")
                continue  # Skip to the next website if there's an error

        # Save results if there is any SERP data
        if serp_data:
            json_file_path = f'{media_type.capitalize()}/{state}/{media_type}_articles_{state}_{year}.jsonl.gz'
            try:
                with gzip.open(json_file_path, 'wt', encoding='utf-8') as jsonl_gzip_file:
                    for entry in serp_data:
                        jsonl_gzip_file.write(json.dumps(entry) + '\n')
                logging.info(f'Saved SERP data for {state} in {year} to {json_file_path}')
            except OSError as e:
                logging.error(f"Error saving data to {json_file_path}: {e}")

    # Log execution time for each state
    key_end_time = time.time()
    key_execution_time = key_end_time - key_start_time
    logging.info(f'Execution time for state {state}: {key_execution_time:.2f} seconds.')

    with open(execution_times_file_path, 'a') as execution_times_file:
        execution_times_file.write(f'State {state}: {key_execution_time:.2f} seconds\n')

# Log overall execution time
overall_end_time = time.time()
overall_execution_time = overall_end_time - overall_start_time
logging.info(f'Total execution time: {overall_execution_time:.2f} seconds.')

with open(execution_times_file_path, 'a') as execution_times_file:
    execution_times_file.write(f'Overall: {overall_execution_time:.2f} seconds\n')

