These python-based scripts were created to support automation of digital preservation workflows at the [University of the Arts (UAL) London Archives and Special Collections Centre](https://www.arts.ac.uk/students/library-services/special-collections-and-archives/archives-and-special-collections-centre). The project was developed as part of completing the Postgraduate Certification at Birbeck, University of London, under supervision of [Abul Hasan](https://abulhasanbbk.github.io/). 

## What this project is

This project brings together three programmes that focus on pre-ingest workflows and support the following key tasks: 

### (1) Compare directories (compare_hashes.py) 

This script compares content between two file directories based on comparison of their MD5 checksums. The script generates a CSV log that identifies what content is duplicated across directories versus content that is unique to one of the directories. The script also generates individual CSV logs for each of the directories listing their MD5 checksums to support any further and ongoing digital collections management. 

### (2) Safely copy content (safe_copy.py) 

Building on compare_hashes.py, this script safely copies content from one directory (source) to another directory (destination). It registers each successful copy process with a timestamp, comparing source/destination MD5 checksums, and outputs this information as a CSV log. Any errors and/or bottlenecks can be identified using the log. 

### (3) Structure content into Preservica-friendly folder structures (structure_SIPs, with utilities) 

Building on both compare_hashes.py and safe_copy.py, this suite of scripts copies over content into a folder structure acceptable to the digital preservation system Preservica. It interprets user specifications for (1) the UAL cataloguing convention (museums [TMS], libraries [Koha] or archives [Calm] and (2) the desired structure (standard or multi-asset PAX). It then creates the appropriate Preservica-friendly folder structure (with appropriate naming convention) and copies content into this required structure. As with safe_copy.py, this programme registers each successful copy process with a timestamp, comparing source/destination MD5 checksums, and outputs this information as a CSV log. Any errors and/or bottlenecks can be identified using the log. 

 

## Who the project is for and why it might be useful 

This project was created with fellow digital archivists and collections managers in mind. It responds to the need for archivists to automate tedious tasks whilst applying scripts that can meet certain archival standards and digital preservation good practice. A priority when developing this project was to ensure that integrity checking was integrated into every programme.  

Programmes (1) and (2) are likely to be useful to any service, regardless of your organisation’s digital preservation maturity. The capacity to compare between and safely copy across directories, with integrity checking, is foundational for many services undertaking pre-ingest tasks. 

Programme (3) responds to the idiosyncracies of the UAL cataloguing environment. However the general logic of the programme could certainly be adapted by other services using Preservica to more readily structure their content for ingest to Preservica. Otherwise, services may find tools like [Bagger](https://github.com/LibraryOfCongress/bagger?tab=readme-ov-file) just as useful. 

## How you can get started with this project 

You will need to have Python 3.12 on your device. 

With python downloaded, you can get started by downloading whichever script (or suite of scripts) you’d like to use.  

### (1) Compare directories (compare_hashes.py) 

You’ll need to know the paths of the two directories you’d like to compare. Download and ensure the compare_hashes.py script is saved in a location that can access these directories. Open your shell interface, ensuring you are in the directory where your script is saved and run: 
```
python compare_hashes.py 
```
Enter the path of each directory you’d like to compare. The relevant CSV logs will be generated following full programme run in a folder titled ‘compare_logs’ which will be saved in the same location that you’ve saved the compare_hashes.py script. 

### (2) Safely copy content (safe_copy.py) 

You’ll need to know the paths of your source and destination directories. Download and ensure the safe_copy.py script is saved in a location that can access these directories. Open your shell interface, ensuring you are in the directory where your script is saved and run: 
```
python safe_copy.py 
```
Enter the path of source and destination directories. The relevant CSV logs will be generated following full programme run in a folder titled ‘copy_logs’ which will be saved in the same location that you’ve saved the safe_copy.py script. 

### (3) Structure content into Preservica-friendly folder structures (structure_SIPs, with utilities) 

You’ll be unlikely to use this script without some tweaks unless you’re based at UAL.  

If based at UAL, you’ll need to know the paths of your source and destination directories. Download and ensure all scripts from the structures_SIPs folder are saved in a location that can access these directories. Open your shell interface, ensuring you are in the directory where your script is saved and run: 
```
python structure_SIPs.py 
```
Enter the path of source and destination directories. Enter the cataloguing system the content has been catalogued in, then enter the type of Preservica-friendly folder strucutre you need (Standard or PAX). The relevant CSV logs will be generated following full programme run in a folder titled ‘copy_logs’ which will be saved in the same location that you’ve saved the structure_SIPs.py and utilities scripts. 

 

## Maintenance and contribution 

I developed this project as part of completing the Postgraduate Certification at Birbeck, University of London. Maintenance is not currently part of my core duties. However, if you have any questions about this project, would like to suggest a tweak or are having trouble using the project, I would be happy to discuss this with you. Please contact me via the UAL Archives and Special Collections Centre at [archives@arts.ac.libanswers.com](mailto:archives@arts.ac.libanswers.com).

 

## Acknowledgements 

Thank you to Abul Hasan for your knowledgeable supervision of this project. 

Thank you to my Archives and Special Collections Centre colleagues (Georgina Orgill, Elisabeth Thurlow, Lucy Parker and Sarah Mahurter) for supporting and engaging with this project during development, particularly during the user testing phase. 

Thank you to my fellow participants in the Digital Preservation Coalition (DPC) / BitCurator Python Study Groups Cohort 2 - Group 21 (Suzy Murray, Sarah Gentile, Annabel Walz, Treasa Harkin, Jack McConchie, Tom Emsom, Michael Whitmore) and our generous supervisor Scott Prater for beginning the seed for [secureCopyFile.py](https://github.com/Digital-Preservation-Coalition/PythonStudyGroups/blob/main/2024%20Cohort%202/Group%2021/secureCopyFile.py) that inspired and encouraged me to continue our work.

Thank you to the UAL Libraries and Student Service Staff Development Fund, the Digital Preservation Coalition Career Development Fund and The National Archives Skills Bursary for supporting my participation on the PgCert Applied Data Science, without which this project would not have been possible. 
