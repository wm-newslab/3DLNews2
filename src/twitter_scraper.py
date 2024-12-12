import argparse
import re
import time
import gzip
import json
import os
from urllib.parse import urlparse
from playwright.sync_api import sync_playwright
from scrape_twitter import get_auth_twitter_pg
from scrape_twitter import get_search_tweets


def extract_tweet_info(tweet):
    return {
        "id_str": tweet.get("id_str", ""),
        "text": tweet.get("text", ""),
        "created_at": tweet.get("created_at", "")
    }


def create_directory(directory_path):
    if not os.path.exists(directory_path):
        try:
            os.makedirs(directory_path)
            print(f"Directory '{directory_path}' created successfully.")
        except OSError as e:
            print(f"Error creating directory '{directory_path}': {e}")
    else:
        print(f"Directory '{directory_path}' already exists.")


def extract_links(tweet):
    entities_urls = tweet.get("entities", {}).get("urls", [])
    if entities_urls:
        return [url["expanded_url"] for url in entities_urls if "expanded_url" in url]

    text = tweet.get("text", "")
    url_pattern = r'https?://\S+'
    urls = re.findall(url_pattern, text)
    return urls


def main():
    parser = argparse.ArgumentParser(description='Scrape tweets for various media types.')
    parser.add_argument('media_type', type=str, choices=['newspaper', 'tv', 'radio', 'broadcast'],
                        help='The type of media to process (newspaper, tv, radio, broadcast).')
    parser.add_argument('start_year', type=int, help='The start year for the search range.')
    parser.add_argument('end_year', type=int, help='The end year for the search range.')
    parser.add_argument('sleep_sec', type=float, help='The number of seconds to sleep between requests.')
    parser.add_argument('media_file', type=str, help='The path to the media JSON gzip file.')
    parser.add_argument('max_tweets', type=int, help='The maximum number of tweets to scrape.')

    args = parser.parse_args()

    media_type = args.media_type
    start_year = args.start_year
    end_year = args.end_year
    sleep_sec = args.sleep_sec
    media_file = args.media_file
    max_tweets = args.max_tweets

    playwright = sync_playwright().start()
    browser_dets = get_auth_twitter_pg(playwright)

    if len(browser_dets) != 0:
        with gzip.open(media_file, 'rt', encoding='utf-8') as file:
            data = json.load(file)

        execution_times_file_path = f'{media_type.capitalize()}/execution_times.txt'
        create_directory(f'{media_type.capitalize()}')

        for key in data.keys():
            key_start_time = time.time()

            media_org = data[key]

            create_directory(f'{media_type.capitalize()}/{key}')

            for year in range(start_year, end_year + 1):
                scraped_tweets = []
                json_file_path = f'{media_type.capitalize()}/{key}/{media_type}_articles_{key}_{year}.jsonl.gz'
                print(json_file_path)
                if not os.path.isfile(json_file_path):
                    print(f"File '{json_file_path}' does not exist.")
                    for media_website in media_org:
                        try:
                            query = f'"{media_website}" until:{year}-12-31 since:{year}-01-01'
                            tweets_data = get_search_tweets(browser_dets, query, max_tweets=max_tweets)
                            tweets = tweets_data.get('tweets', [])

                            for tweet in tweets:
                                links = extract_links(tweet)
                                if len(links) != 0:
                                    tweet_info_dict = {"tweet": tweet, "query": query, "links": links}
                                    scraped_tweets.append(tweet_info_dict)
                        except Exception as e:
                            print(e)
                            print("\n------------------------\n")
                            playwright.stop()
                            print("Closing the browser...")
                            playwright = sync_playwright().start()
                            print("Reopening the browser...")
                            browser_dets = get_auth_twitter_pg(playwright)
                            continue

                        time.sleep(sleep_sec)

                    if len(scraped_tweets) > 0:
                        with gzip.open(json_file_path, 'wt') as outfile:
                            for tweet_info_dict in scraped_tweets:
                                json_object = json.dumps(tweet_info_dict, ensure_ascii=False)
                                outfile.write(json_object + '\n')

            key_end_time = time.time()

            key_execution_time = key_end_time - key_start_time
            print(f'Execution time for key {key}: {key_execution_time} seconds.')

            with open(execution_times_file_path, 'a') as execution_times_file:
                execution_times_file.write(f'Key {key}: {key_execution_time} seconds\n')

    playwright.stop()


if __name__ == "__main__":
    main()
