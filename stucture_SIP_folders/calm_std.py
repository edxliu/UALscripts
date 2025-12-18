import os.path
import csv
import datetime
import shutil

from structure_SIPs_utils import (generate_md5)

# Identify catalogue reference numbers in filename prefix in order to create folders based on these prefixes.

def get_folder_names_calm_std(source_path):
    name, _ = os.path.splitext(source_path)
    parts = name.split('-')

    # At least two parts required to build hierarchy
    if len(parts) >= 4:
        top_folder = '-'.join(parts[:-1])  # e.g. CAMB-1-17-2
        full_folder = name                 # e.g. CAMB-1-17-2-2
        return os.path.join(top_folder, full_folder)
    else:
        # Fallback: single folder named after filename without extension
        return name


# Securely restructure content into Preservica-friendly folder structures from input path, logging progress through MD5 hash generation and date/time of completion for each file along the way.

def secure_copy(path1, path2, csv_path):
    source_data = {}
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_data[row['Relative_SourcePath']] = {
                'Source_MD5': row['Source_MD5']
            }

    for root, _, files in os.walk(path1):
        for f in files:
            source_file = os.path.join(root, f)
            relative_path = os.path.relpath(source_file, path1)

            # Determine folder name using refined prefix rule
            dynamic_parent_folder = get_folder_names_calm_std(f)
            destination_folder = os.path.join(path2, dynamic_parent_folder)
            os.makedirs(destination_folder, exist_ok=True)

            destination_file = os.path.join(destination_folder, f)
            shutil.copy2(source_file, destination_file)

            dest_file_hash = generate_md5(destination_file)
            current_date_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

            if relative_path in source_data:
                source_data[relative_path].update({
                    'Destination_MD5': dest_file_hash,
                    'Date_time': current_date_time
                })
            else:
                source_data[relative_path] = {
                    'Source_MD5': '',
                    'Destination_MD5': dest_file_hash,
                    'Date_time': current_date_time
                }

    # Write updated CSV
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        field_labels = ['Relative_SourcePath', 'Source_MD5', 'Destination_MD5', 'Date_time']
        writer = csv.DictWriter(csvfile, fieldnames=field_labels)
        writer.writeheader()
        for path, data in source_data.items():
            writer.writerow({
                'Relative_SourcePath': path,
                'Source_MD5': data.get('Source_MD5', ''),
                'Destination_MD5': data.get('Destination_MD5', ''),
                'Date_time': data.get('Date_time', '')
            })
