import os.path
import sys
import hashlib
import csv
import datetime


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

# Write filepaths and generated file hashes to individual CSV files.
def write_hashes_to_csv(file_list, base_folder, csv_path):
    with open(csv_path, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Relative_Path', 'MD5_Hash'])

        for file_path in file_list:
            relative_path = os.path.relpath(file_path, base_folder)
            file_hash = generate_md5(file_path)
            writer.writerow([relative_path, file_hash])

# Compare the logs to identify discrepancies in the file directories.
def compare_hash_csvs(csv1, csv2):
    def load_csv(path):
        with open(path, 'r', encoding='utf-8') as f:
            return {rows[0]: rows[1] for rows in csv.reader(f) if rows and rows[0] != 'Relative_Path'}

    hash1 = load_csv(csv1)
    hash2 = load_csv(csv2)

    all_keys = set(hash1.keys()).union(set(hash2.keys()))
    evaluation = []

    for key in sorted(all_keys):
        value1 = hash1.get(key)
        value2 = hash2.get(key)

        if value1 is None:
            status = f'Unique - Only in {no_space_name(folder_2)}'
        elif value2 is None:
            status = f'Unique - Only in {no_space_name(folder_1)}'
       # elif value1 != value2:
       #     status = 'Hash mismatch'
        else:
            status = 'Duplicate - Present in both folders'

        evaluation.append((key, value1 or '', value2 or '', status))

    return evaluation

# Write results from hash comparison to a new CSV log.
def write_hash_comparison_to_csv(hash_evaluation, output_path):
    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['Relative_Path', 'Folder1_MD5', 'Folder2_MD5', 'Status'])
        for evaluation in hash_evaluation:
            writer.writerow(evaluation)

###############################################
# Execution of functions using user-specified paths occurs below, provided the user supplies valid paths.

# Get user variables (folder names).
folder_1 = input('Enter first folder file path for analysis: ').strip()
folder_2 = input('Enter second folder file path for analysis: ').strip()

if check_path_exists(folder_1) and check_path_exists(folder_2):
    print('\nBoth folders exist, proceeding with checksum generation...')

    # Set up file list variables.
    files_1 = list_all_files(folder_1)
    files_2 = list_all_files(folder_2)

    # Set up CSV filenames to write to.
    script_dir = get_script_directory()
    logs_dir = os.path.join(script_dir, "compare_logs")
    os.makedirs(logs_dir, exist_ok=True)
    today_date = datetime.date.today().strftime("%d-%m-%Y")
    csv1_path = os.path.join(logs_dir, f"{no_space_name(folder_1)}_hashes_{today_date}.csv")
    csv2_path = os.path.join(logs_dir, f"{no_space_name(folder_2)}_hashes_{today_date}.csv")
    report_path = os.path.join(logs_dir, f"comparison_report_{no_space_name(folder_1)}_vs_{no_space_name(folder_2)}_{today_date}.csv")

    # Run function to write hashes for user input into CSV files.
    print('\n Creating CSV logs with MD5 checksums for every file in each folder...')
    write_hashes_to_csv(files_1, folder_1, csv1_path)
    write_hashes_to_csv(files_2, folder_2, csv2_path)

    # Set up variables to establishes discrepancies.
    evaluation = compare_hash_csvs(csv1_path, csv2_path)

    # Deploy function to write reports for any discrepancies identified.
    print(f'\n Writing full comparison report to {report_path}...')
    write_hash_comparison_to_csv(evaluation, report_path)

    for diff in evaluation:
        rel_path, hash1, hash2, status = diff
        print(f'- {rel_path} | {status}')

else:
    print('\n One or both folder paths are invalid. Exiting...')
    sys.exit(1)
