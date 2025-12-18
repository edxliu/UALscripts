import os
import shutil
import sys
import hashlib
import csv

# Below are functions that are common to all or most use-cases, regardless of catalogue/structure input.

# Return the directory where the calling script is located.
def get_script_directory():
    print('\n Locating script directory...')
    return os.path.dirname(os.path.realpath((sys.argv[0])))

# Return 'True' if the path supplied exists on the disk.
def check_path_exists(path: str):
    print('\n Checking for existence of "' + path + "'...")
    return os.path.exists(path)


# Recursively walk a directory and return a list of all file paths within a directory.
def list_all_files(folder_path):
    all_files = []
    for root, _, files in os.walk(folder_path):
        for f in files:
            all_files.append(os.path.join(root, f))
    return all_files


# Generate MD5 hashes for folder contents.
def generate_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        chunk = f.read(4096)
        while len(chunk) > 0:
            hasher.update(chunk)
            chunk = f.read(4096)
    return hasher.hexdigest()


# Ensure there are no spaces or issue characters in filename for CSV log file by stripping directories and replacing spaces with underscores.
def no_space_name(path):
    return os.path.basename(os.path.normpath(path)).replace(" ", "_")


# Create a CSV to write filepaths and file hashes to.
def write_source_hashes_to_csv(file_list, base_folder, csv_path):

    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Relative_SourcePath', 'Source_MD5'])

        for file_path in file_list:
            relative_path = os.path.relpath(file_path, base_folder)
            file_hash = generate_md5(file_path)
            writer.writerow([relative_path, file_hash])

# Below are functions shared across use-cases that require a multi-asset ('PAX') folder structure.

# Mappings to support PAX folder structuring, determining what file formats there are and whether they are access/preservation formats.
file_format_mapping = {
    'image': ['jpeg', 'jpg', 'png', 'tiff', 'tif'],
    'document': ['doc', 'docx', 'pdf'],
    'audio': ['mp3', 'wav', 'aiff'],
    'video': ['mp4', 'mkv', 'mov']
}

representation_mapping = {
    'access': ['jpeg', 'jpg', 'png', 'pdf', 'mp3', 'mp4'],
    'preservation': ['tiff', 'tif', 'doc', 'docx', 'wav', 'aiff', 'mkv', 'mov']
}

# Based on above mapping, extract the file format.
def get_file_format(ext):
    for file_format, extensions in file_format_mapping.items():
        if ext.lower() in extensions:
            return file_format.capitalize()
    return "Unknown"

# Based on above mapping, interpret whether file formats present and access or preservation copies.
def determine_representation(ext):
    ext = ext.lower()
    if ext in representation_mapping['access']:
        return 'Representation_Access'
    elif ext in representation_mapping['preservation']:
        return 'Representation_Preservation'
    return None

# Distribute file into DPS-friendly multi-part asset (PAX) folder structure.
def distribute_file(source_file, filename_prefix, base_output_dir, *, legacy_nested=False):
    extension = source_file.split('.')[-1].lower()
    representation = determine_representation(extension)

    if not representation:
        return None

    file_format = get_file_format(extension)

    if legacy_nested:
        top_level = os.path.join(base_output_dir, filename_prefix)
        pax_root = os.path.join(top_level, f"{filename_prefix}.pax")
    else:
        pax_root = os.path.join(base_output_dir, f"{filename_prefix}.pax")

    destination_folder = os.path.join(pax_root, representation, file_format)
    os.makedirs(destination_folder, exist_ok=True)

    shutil.copy2(source_file, os.path.join(destination_folder, os.path.basename(source_file)))
    return destination_folder

# Compare hashes between source and destination directories, reporting on any missing/corrupt files in the log file and print statement.
def compare_hashes(csv_path):
    rows = []

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            path1 = row.get('Source_MD5', '')
            path2 = row.get('Destination_MD5', '')
            if not path1:
                status = 'Missing source hash'
            elif not path2:
                status = 'Missing destination hash'
            elif path1 != path2:
                status = 'Hash mismatch'
            else:
                status = 'MATCH'
            row['Status'] = status
            rows.append(row)

    # Add to CSV to include match_status
    with open(csv_path, 'w', newline='', encoding='utf-8') as f:
        field_labels = rows[0].keys()
        writer = csv.DictWriter(f, fieldnames=field_labels)
        writer.writeheader()
        writer.writerows(rows)

    # Write print statement to report on copy workflow results.
    mismatches = [r for r in rows if r['Status'] != 'MATCH']

    if mismatches:
        print('\n Mismatched or missing files detected:')
        for entry in mismatches:
            print(f" - {entry['Relative_SourcePath']}: Source Hash = {entry['Source_MD5']}, "
                  f"Destination Hash = {entry['Destination_MD5']}, Status = {entry['Status']}")
    else:
        print('\n All files copied and verified successfully.')