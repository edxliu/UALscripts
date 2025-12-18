import os.path
import sys
import csv
import datetime
import shutil

# Import key shared function (hash generation, file distribution) from structure_SIPs_utils.py.
from structure_SIPs_utils import (
    generate_md5,
    distribute_file
)

# Identify Koha reference numbers in filename prefix for OPEX validation.
def get_folder_names_koha_std(source_path: str) -> str:
    # filename without directories or extension
    name = os.path.splitext(os.path.basename(source_path))[0]
    # If there's a single trailing lowercase letter, drop it
    if name and 'a' <= name[-1] <= 'z':
        name = name[:-1]
    # Take only the leading digit run
    i = 0
    while i < len(name) and name[i].isdigit():
        i += 1
    # Return the numeric prefix if present; otherwise, return the original name
    return name[:i] if i > 0 else name


# Ensure that an OPEX file is present and corresponds to any unique TMS reference numbers found.
def validate_opex_files_pax(source_folder, file_list):
    unique_prefixes = set()

    for file_path in file_list:
        filename = os.path.basename(file_path)
        prefix = get_folder_names_koha_std(filename)
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
            ext = f.split('.')[-1].lower()

            # Get filename prefix for folder naming
            filename_prefix = get_folder_names_koha_std(f)
            parent_folder = os.path.join(path2, filename_prefix)
            os.makedirs(parent_folder, exist_ok=True)

            # If it's an OPEX file, determine correct parent folder
            if ext == 'opex':
                # Place .opex metadata files alongside the corresponding .pax folder
                destination_file = os.path.join(parent_folder, f)
                shutil.copy2(source_file, destination_file)

            else:
                # Distribute by representation + media type
                dest_folder = distribute_file(source_file, filename_prefix, parent_folder)
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
