import os.path
import sys
import hashlib
import csv
import datetime
import shutil

# Define key functions that will be executed in this script.

# Locate the directory that the safe_copy.py is located in.
def get_script_directory():
    print('\n Locating script directory...')
    return os.path.dirname(os.path.realpath((sys.argv[0])))

# Ensure a path exists.
def check_path_exists(path: str):
    print('\n Checking for existence of "' + path + "'...")
    return os.path.exists(path)

# Obtain list of all files within folder.
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

# Ensure there are no spaces or issue characters in filename for CSV log file.
def no_space_name(path):
    return os.path.basename(os.path.normpath(path)).replace(" ", "_")

# Write filepaths and file hashes to CSV files.
def write_source_hashes_to_csv(file_list, base_folder, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Relative_SourcePath', 'Source_MD5'])

        for file_path in file_list:
            relative_path = os.path.relpath(file_path, base_folder)
            file_hash = generate_md5(file_path)
            writer.writerow([relative_path, file_hash])

# Securely copy content from source (path1) to destination (2), logging progress through MD5 hash generation and date/time of completion for each file along the way.
def secure_copy(path1, path2, csv_path):
    # Load data relating to source files in the CSV log.
    source_data = {}
    with open(csv_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            source_data[row['Relative_SourcePath']] = {
                'Source_MD5': row['Source_MD5']
            }

        # Walk through source folder, copy files with metadata and generate MD5 hash for destination files.
        for root, _, files in os.walk(path1):
            for f in files:
                source_file = os.path.join(root, f)
                relative_path = os.path.relpath(source_file, path1)
                destination_file = os.path.join(path2, relative_path)

                os.makedirs(os.path.dirname(destination_file), exist_ok=True)
                shutil.copy2(source_file, destination_file)

                dest_file_hash = generate_md5(destination_file)
                current_date_time = datetime.datetime.now().strftime("%d-%m-%Y %H:%M:%S")

                if relative_path in source_data:
                    source_data[relative_path]['Destination_MD5'] = dest_file_hash
                    source_data[relative_path]['Date_time'] = current_date_time
                else:
                    # If path not found (which shouldn't happen), log it anyway.
                    source_data[relative_path] = {
                        'Source_MD5': '',
                        'Destination_MD5': dest_file_hash,
                        'Date_time': current_date_time
                    }

    # Write destination data to the same CSV log.
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


# Compare hashes and report on any missing/corrupt files in the log file and print statement.
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


###############################################
# Execution of functions using user-specified paths occurs below, provided the user supplies valid paths.

# Get user variables (folder names).
source = str(input('Enter source path name (i.e. the content you want to copy): ').strip())
destination = str(input('Enter destination file path (i.e. the place you want to copy to): ').strip())

if check_path_exists(source) and check_path_exists(destination):
    print('\n Source folder and destination identified, proceeding with checksum generation of source files...')

    # Set up source file list variable.
    files_1 = list_all_files(source)

    # Set up folder and its location to write CSV log to.
    today_date = datetime.date.today().strftime("%d-%m-%Y")
    source_label = os.path.basename(source)
    destination_label = os.path.basename(destination)

    script_dir = get_script_directory()
    source_parent_dir = os.path.dirname(os.path.normpath(source))
    logs_dir = os.path.join(script_dir, "copy_logs")
    os.makedirs(logs_dir, exist_ok=True)

    log_file = os.path.join(logs_dir,
                            f"copyLog_{no_space_name(source_label)}_to_{no_space_name(destination_label)}_{today_date}.csv")

    # Run function to write hashes for user input source files into a CSV file.
    print('\n Creating CSV logs with MD5 checksums for every file in each source folder...')
    write_source_hashes_to_csv(files_1, source, log_file)

    # Copy source files and write copies to destination filepath, logging progress in a CSV log file.
    print('\n Copying content from source folder to destination folder, logging progress in CSV file (in parent folder of your source directory)...')
    secure_copy(source, destination, log_file)

    # Compare hashes and report on any missing/corrupt files in the  CSV log file and print statement.
    print('\n Quality checking secure copy workflow...')
    compare_hashes(log_file)

else:
    print('\n One or both folder paths are invalid. Exiting...')
    sys.exit(1)