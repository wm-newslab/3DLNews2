import os
import gzip
import json
import csv
import argparse

# --------- Argument Parser Setup ---------
parser = argparse.ArgumentParser(description="Extract filtered news data from JSONL.GZ files and convert to CSV.")
parser.add_argument('--base-dir', type=str, default='.', help='Base directory containing Google and Twitter folders.')
parser.add_argument('--platforms', nargs='*', default=['1-Google', '2-Twitter'], help='Platforms to include: Google, Twitter.')
parser.add_argument('--media-types', nargs='*', default=['1-Newspaper', '2-Radio', '3-TV', '4-Broadcast'], help='Media types to include: newspaper, radio, tv, broadcast.')
parser.add_argument('--years', nargs='*', type=int, help='Years to include, e.g., 2020 2021 2022.')
parser.add_argument('--metadata', nargs='*', help='Fields to extract (id and file_path included by default).')

args = parser.parse_args()

# --------- Configuration Defaults ---------
default_fields = ['id', 'link', 'expanded_url', 'publication_date', 'title', 'content']
fields_to_extract = ['id', 'file_path'] + (args.metadata if args.metadata else default_fields)

# --------- Data Extraction Function ---------
def extract_jsonl_gz_to_csv(full_media_path, platform, media_type):
    print(f"\n[INFO] Starting extraction for: {full_media_path}")

    input_dir = os.path.join(full_media_path, 'v5_preprocessed_state')

    if not os.path.exists(input_dir):
        print(f"[WARN] Skipping {platform} - directory not found: {input_dir}")
        return

    output_dir = os.path.join('results', platform)
    os.makedirs(output_dir, exist_ok=True)

    output_csv_path = os.path.join(output_dir, f"{media_type}.csv")
    all_extracted_rows = []

    for state in sorted(os.listdir(input_dir)):
        state_path = os.path.join(input_dir, state)
        if not os.path.isdir(state_path):
            continue

        file_list = os.listdir(state_path)
        print(f"[INFO] Processing state '{state}' with {len(file_list)} files...")

        for i, file_name in enumerate(file_list):
            if args.years:
                year_match = next((str(y) for y in args.years if str(y) in file_name), None)
                if not year_match:
                    continue

            file_path = os.path.join(state_path, file_name)

            try:
                with gzip.open(file_path, 'rt', encoding='utf-8') as f:
                    for line in f:
                        try:
                            record = json.loads(line)

                            if not record.get("is_news_article"):
                                continue

                            row = {
                                'id': record.get("id"),
                                'file_path': file_path
                            }

                            for field in fields_to_extract:
                                if field not in row:
                                    row[field] = record.get(field, "")

                            all_extracted_rows.append(row)

                        except json.JSONDecodeError:
                            continue
            except Exception as e:
                print(f"[ERROR] Failed to process {file_path}: {e}")

    if all_extracted_rows:
        print(f"[INFO] Writing total {len(all_extracted_rows)} records to CSV: {output_csv_path}")
        with open(output_csv_path, 'w', newline='', encoding='utf-8') as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=fields_to_extract)
            writer.writeheader()
            writer.writerows(all_extracted_rows)
    else:
        print(f"[INFO] No valid news articles found for: {platform}/{media_type}")


# --------- Main Execution Loop ---------
print("[INFO] Starting extraction process...")
for platform in args.platforms:
    media_root = os.path.join(args.base_dir, platform)
    if not os.path.exists(media_root):
        print(f"[WARN] Skipping missing platform directory: {media_root}")
        continue

    for media_type in args.media_types:
        full_media_path = os.path.join(media_root, media_type)
        print(f"\n[INFO] Scanning platform '{platform}', media folder '{media_type}'")
        extract_jsonl_gz_to_csv(full_media_path, platform, media_type)

print("\n[INFO] Extraction complete.")
