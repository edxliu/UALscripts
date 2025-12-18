import os.path
import re
import sys
import csv
import datetime
import shutil

# Import key shared function (hash generation, file distribution) from structure_SIPs_utils.py.
from structure_SIPs_utils import (
    generate_md5,
    distribute_file
)

# Identify TMS reference numbers in filename prefix for OPEX validation.
def get_folder_names_tms_std(source_path):
    # Match a prefix ending with digits, possibly followed by a single lowercase letter
    match = re.match(r'^(.*\D)?(\d+)[a-z]?$', '.'.join(source_path.split('.')[:-1]))
    if match:
        prefix_base, number = match.groups()
        return f"{prefix_base}{number}"
    else:
        return '.'.join(source_path.split('.')[:-1])


# Identify amended TMS PAX reference numbers in filename prefix in order to create parent folders based on these prefixes.
def get_parent_folder_names_tms_pax(source_path):
    # Match lowercase letter before the final dot (e.g., abcD.txt → match 'c')
    match = re.search(r'([a-z])(?=\.[^.]+$)', source_path)
    if match:
        cutoff_index = match.start()
        return source_path[:cutoff_index]
    else:
        base = '.'.join(source_path.split('.')[:-1])
    return f'{base}.pax'


# Ensure that an OPEX file is present and corresponds to any unique TMS reference numbers found using sets.
def validate_opex_files_pax(source_folder, file_list, destination_folder):
    unique_prefixes = set()

    for file_path in file_list:
        filename = os.path.basename(file_path)

        if not filename.lower().endswith('.opex'):
            prefix = get_folder_names_tms_std(filename)
            unique_prefixes.add(prefix)

    opex_files = [f for f in os.listdir(source_folder)
                  if f.lower().endswith('.opex') and os.path.isfile(os.path.join(source_folder, f))]

    valid_opex_prefixes = set()

    for opex in opex_files:
        base = opex[:-5]  # strip '.opex'

        # Meet use-cases where OPEX file is in a ranged format by identifying presence of hyphen.
        if '-' in base:
            match = re.match(r'^(.*?)(\d+)-(\d+)$', base)
            if match:
                prefix_part, start_str, end_str = match.groups()
                start, end = int(start_str), int(end_str)
                for i in range(start, end + 1):
                    valid_opex_prefixes.add(f"{prefix_part}{i}")
            else:
                print(f'Warning: Could not parse OPEX range file {opex}')

        else:
            valid_opex_prefixes.add(base)

    missing_opex = []

    for prefix in unique_prefixes:
        if prefix not in valid_opex_prefixes:
            missing_opex.append(prefix)
            continue

    if missing_opex:
        print('\nError: The following reference prefixes are missing required OPEX files:')
        for prefix in missing_opex:
            print(f' - {prefix}')
        sys.exit('\nAborting due to missing metadata (OPEX) files.\n')

    for opex in opex_files:
        folder_name = os.path.splitext(opex)[0]
        folder_path = os.path.join(destination_folder, folder_name)
        os.makedirs(folder_path, exist_ok=True)


# Securely reorganise content into Preservica-friendly folder structures from input path, logging progress through MD5 hash generation and date/time of completion for each file along the way.

def secure_copy(path1, path2, csv_path):

    opex_files = [f for f in os.listdir(path1)
        if f.lower().endswith('.opex') and os.path.isfile(os.path.join(path1, f))]

    exact_opex_prefixes = set()
    ranged_groups = []

    for opex in opex_files:
        base = opex[:-5]
        if '-' in base:
            m = re.match(r'^(.*?)(\d+)-(\d+)$', base)
            if m:
                prefix_part, start_str, end_str = m.groups()
                ranged_groups.append((base, prefix_part, int(start_str), int(end_str)))
        else:
            exact_opex_prefixes.add(base)

    # Account for cases where OPEX files cover a range of discrete reference number.
    group_parent_map = {}  # {"PH.681.1": "PH.681.1-3", ...}
    for group_label, prefix_part, start, end in ranged_groups:
        for i in range(start, end + 1):
            indiv = f"{prefix_part}{i}"
            if indiv not in exact_opex_prefixes:
                group_parent_map[indiv] = group_label

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

            item_prefix = get_parent_folder_names_tms_pax(f).replace('.pax', '')

            if ext == 'opex':
                parent_label = item_prefix
            else:
                parent_label = group_parent_map.get(item_prefix, item_prefix)

            parent_folder = os.path.join(path2, parent_label)
            os.makedirs(parent_folder, exist_ok=True)

            # Determine correct parent folder for any opex files.
            if ext == 'opex':
                destination_file = os.path.join(parent_folder, f)
                shutil.copy2(source_file, destination_file)
            else:
                dest_folder = distribute_file(source_file, item_prefix, parent_folder)
                if dest_folder is None:
                    continue
                destination_file = os.path.join(dest_folder, f)

            # Verify and log hash and date/time in CSV log.
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