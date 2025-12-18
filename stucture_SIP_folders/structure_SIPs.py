import os
import sys
import datetime

# Import key shared functions from structure_SIPs_utils.py.
from structure_SIPs_utils import (
    get_script_directory,
    check_path_exists,
    list_all_files,
    no_space_name,
    write_source_hashes_to_csv,
    compare_hashes
)

# Import all handlers to determine script behaviour based on cataloguing system (TMS, Koha or Calm) and intended folder structure (Standard or PAX).
from tms_std    import validate_opex_files as validate_tms_std,    secure_copy as secure_copy_tms_std
from tms_pax    import validate_opex_files_pax as validate_tms_pax,    secure_copy as secure_copy_tms_pax
from koha_std   import validate_opex_files as validate_koha_std,   secure_copy as secure_copy_koha_std
from koha_pax   import validate_opex_files_pax as validate_koha_pax,   secure_copy as secure_copy_koha_pax
from calm_std   import secure_copy as secure_copy_calm_std
from calm_pax   import secure_copy as secure_copy_calm_pax

# Function to prompt user for inputs for source/destination directories, cataloguing system and intended folder structure, which will determine appropriate handlers as outlined above.
def get_user_inputs():
    source = input('Enter source path name (i.e. the content you want to restructure to be Preservica-friendly): ').strip()
    destination = input('Enter destination file path (i.e. the place you want your Preservica-friendly folder structure to be created): ').strip()
    # Get user variable for catalogue using a controlled vocabulary.
    acceptable_catalogue_values = ['TMS', 'Koha', 'Calm']
    while True:
        catalogue = input('Which system has the content been catalogued in? (TMS / Koha / Calm): ').strip()
        if catalogue in acceptable_catalogue_values:
            break
        else:
            print(
                'Input is not included in options. Please try again -- refer to options in brackets (TMS / Koha / Calm) and be mindful of case.')
    # Get user variable for desired structure using a controlled vocabulary.
    acceptable_structure_values = ['Standard', 'PAX']
    while True:
        structure = input('What type of folder structure do you need? (Standard / PAX): ').strip()
        if structure in acceptable_structure_values:
            break
        else:
            print(
                'Input is not included in options. Please try again -- refer to options in brackets (Standard / PAX) and be mindful of case.')
    return source, destination, catalogue, structure

# Function for main script, which instructs bulk of execution (i.e. validation, organising, copying, logging and integrity checking).
def main():
    source, destination, catalogue, structure = get_user_inputs()

    # Ensure the source/destination paths supplied by user are indeed valid. If not, exit script execution.
    if not (check_path_exists(source) and check_path_exists(destination)):
        print("Source and/or directory path(s) are invalid. Please amend invalid path(s) and rerun script.")
        sys.exit(1)

    files = list_all_files(source)

    # Ensure existence of or create a logs folder in the same location as the main script.
    script_dir = get_script_directory()
    logs_dir = os.path.join(script_dir, 'copy_logs')
    os.makedirs(logs_dir, exist_ok=True)

    # Create a unique log filename for this run of main script.
    today_date = datetime.date.today().strftime("%d-%m-%Y")
    source_label = no_space_name(os.path.basename(source))
    destination_label = no_space_name(os.path.basename(destination))
    log_file = os.path.join(logs_dir,
                            f"copyLog_{source_label}_to_{destination_label}_{today_date}.csv")

    # Write source hashes to the CSV log file.
    write_source_hashes_to_csv(files, source, log_file)

    # For TMS and Koha material, ensure presence of an OPEX metadata file prior to copying any content, using appropriate validation handler.
    if catalogue in ('TMS', 'Koha'):
        if structure == 'Standard':
            validate_tms_std(source, files) if catalogue=='TMS' else validate_koha_std(source, files)
        else:
            validate_tms_pax(source, files, destination) if catalogue=='TMS' else validate_koha_pax(source, files)
    else:  # Calm
        pass

    # Secure copy digital content from source directory to destination directory in accordance with appropriate copy handler, logging progress in the CSV log file.
    if catalogue == 'TMS' and structure == 'Standard':
        secure_copy_tms_std(source, destination, log_file)
    elif catalogue == 'TMS' and structure == 'PAX':
        secure_copy_tms_pax(source, destination, log_file)
    elif catalogue == 'Koha' and structure == 'Standard':
        secure_copy_koha_std(source, destination, log_file)
    elif catalogue == 'Koha' and structure == 'PAX':
        secure_copy_koha_pax(source, destination, log_file)
    elif catalogue == 'Calm' and structure == 'Standard':
        secure_copy_calm_std(source, destination, log_file)
    else:
        secure_copy_calm_pax(source, destination, log_file)

    # Compare hashes from source directory and destination directory to ensure all content has been safely copied over.
    compare_hashes(log_file)

# Execute main script.
if __name__ == '__main__':
    main()