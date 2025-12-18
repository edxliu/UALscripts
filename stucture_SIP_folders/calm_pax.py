import os.path
import csv
import datetime

# Import key shared function (hash generation, file distribution) from structure_SIPs_utils.py.
from structure_SIPs_utils import (
    generate_md5,
    distribute_file
)

# Identify Calm catalogue reference numbers in filename prefix in order to create parent folders based on these prefixes.
def get_folder_names_calm_pax(source_path):
    name, _ = os.path.splitext(source_path)
    parts = name.split('-')

    if len(parts) >= 4:
        top_folder = '-'.join(parts[:-1])  # e.g. CAMB-1-17-2
        full_folder = name  # e.g. CAMB-1-17-2-2
        return os.path.join(top_folder, full_folder)
    else:
        return f"{name}.pax"


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
            ext = f.split('.')[-1].lower()

            # Get filename prefix for folder naming
            filename_prefix = get_folder_names_calm_pax(f).replace(".pax", "")
            dest_folder = distribute_file(source_file, filename_prefix, path2)

            if dest_folder is None:
                continue  # Skip unknown types

            destination_file = os.path.join(dest_folder, f)

            # Verify and log hash and date/time
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

    # Write updated CSV log to support hash comparison and quality assurance.
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