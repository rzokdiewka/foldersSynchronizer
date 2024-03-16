# Functionality

Program that synchronizes two folders: source and replica. Functionality meets the assumptions:

* One-way synchronization - content of the replica folder is modified to match content of the source folder
* Synchronization is performed periodically with default 1h interval which can be customised. In case that
  synchronization takes more than the interval time, it process until the end and next synchronization starts as soon as
  previous one is completed
* File and folders creation, copying or removal operations are logged to a file and to the console output
* Folder paths, synchronization interval and log file path can be provided using the command line arguments

# How to run

Make sure you have `Python 3.9` or newer version installed.

From `main.py` script directory run:

`python main.py -s source_folder_path -r  replica_folder_path -l logs_file_path -i interval_in_seconds`

Check `help` for details about arguments

`python main.py --help`