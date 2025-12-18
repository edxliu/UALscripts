import os.path
import re
import sys
import csv
import datetime
import shutil

# Import key shared function (hash generation) from structure_SIPs_utils.py.
from structure_SIPs_utils import (generate_md5)

# Identify TMS catalogue reference numbers in filename prefix for OPEX validation and to create folders based on these prefixes.
def get_folder_names_tms_std(source_path):
    # Match a prefix ending with digits, possibly followed by a single lowercase letter
    match = re.match(r'^(.*\D)?(\d+)[a-z]?$', '.'.join(source_path.split('.')[:-1]))
    if match:
        prefix_base, number = match.groups()
        return f"{prefix_base}{number}"
    else:
        return '.'.join(source_path.split('.')[:-1])

# Ensure that an OPEX file is present and corresponds to any unique TMS reference numbers found.
def validate_opex_files(source_folder, file_list):
    unique_prefixes = set()

    for file_path in file_list:
        filename = os.path.basename(file_path)
        prefix = get_folder_names_tms_std(filename)
        unique_prefixes.add(prefix)

    missing_opex = []

    for prefix in unique_prefixes:
        expected_opex_filename = f"{prefix}.opex"
        expected_opex_path = os.path.join(source_folder, expected_opex_filename)

        if not os.path.isfile(expected_opex_path):
            missing_opex.append(prefix)

    if missing_opex:
        print(
            "\nError: The following reference prefixes are missing required OPEX files - obtain these files prior to rerunning this script:")
        for prefix in missing_opex:
            print(f" - {prefix}")
        sys.exit("\nAborting due to missing metadata (OPEX) files.\n")


# Securely reorganise content into Preservica-friendly folder structures from input path, logging progress through MD5 hash generation and date/time of completion for each file along the way.
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

            # Determine folder name using function get_folder_names_tms_std(), defined earlier.
            dynamic_parent_folder = get_folder_names_tms_std(f)
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