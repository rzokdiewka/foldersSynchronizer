import argparse
import logging
import os
import shutil
import sys
import time
from hashlib import md5


def has_same_metadata(source_file, replica_file):
    """Compere items modification date and size"""
    return (os.path.getmtime(source_file) == os.path.getmtime(replica_file)
            or os.path.getsize(source_file) == os.path.getsize(replica_file))


def has_same_content(source_file, replica_file):
    """Compere files content"""
    with open(source_file, 'rb') as f:
        source_h = md5(f.read()).hexdigest()
    with open(replica_file, 'rb') as f:
        replica_h = md5(f.read()).hexdigest()
    return source_h == replica_h


def synchronize_files(source_file, replica_file, content_comparison):
    """Checking whether replica file is synchronized with source, if not then perform synchronization"""

    if not os.path.exists(replica_file):
        # if file doesn't exist
        logging.info(f"Replica FILE {replica_file} doesn't exist. Copying source FILE into replica path.")
        shutil.copy2(source_file, replica_file)
    else:
        file_up_to_date = has_same_content(source_file, replica_file) if content_comparison else has_same_metadata(
            source_file, replica_file)

        if not file_up_to_date:
            # if file changed replace it with source file
            logging.info(f"Replica FILE {replica_file} changed. Replacing it with source FILE.")
            shutil.copy2(source_file, replica_file)


def remove_not_existing_items(source_path, replica_path):
    """From replica folder remove items which don't exist in source folder anymore"""
    for f in os.listdir(replica_path):
        # f can be a file or folder name
        source_f = f"{source_path}/{f}"
        replica_f = f"{replica_path}/{f}"
        if not os.path.exists(source_f):
            logging.info(f"Replica {replica_f} doesn't exist in source path. Removing it from replica path.")
            if os.path.isfile(replica_f):
                os.remove(replica_f)
            elif os.path.isdir(replica_f):
                shutil.rmtree(replica_f)


def synchronize_folders(source_path: str, replica_path: str, content_comparison: bool) -> None:
    """Checking whether replica folder is synchronized with source, if not then perform synchronization"""
    if not os.path.exists(replica_path):
        # if replica folder doesn't exist
        logging.info(
            f"Replica PATH {replica_path} doesn't exist. Creating one and copying source path content into it.")
        shutil.copytree(source_path, replica_path)
    else:
        # if replica folder exist then iterate over files/folders in source path
        for f in os.listdir(source_path):
            # f can be a file or folder name
            source_f = f"{source_path}/{f}"
            replica_f = f"{replica_path}/{f}"

            if os.path.isfile(source_f):
                synchronize_files(source_f, replica_f, content_comparison)
            elif os.path.isdir(source_f):
                synchronize_folders(source_f, replica_f, content_comparison)

        # if files or folders aren't in source path
        remove_not_existing_items(source_path, replica_path)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Program that synchronizes two folders: source and replica. Requires to pass arguments.")
    parser.add_argument("-s", "--source", help="(required) path to source folder", required=True)
    parser.add_argument("-r", "--replica", help="(required) path to source folder", required=True)
    parser.add_argument("-l", "--logs", help="(required) path log file", required=True)

    parser.add_argument("-i", "--interval",
                        help="(optional) synchronization interval [s], 3600 by default",
                        default=3600,
                        required=False, type=int)

    parser.add_argument("-c", "--comparison_mode",
                        help="(optional) comparison mode, by default or if set to 'content' files content is compared "
                             "by their hashes comparison (processing time depends on files size). Setting 'metadata' "
                             "means files modification dates and sizes are compared (it shortens synchronization time "
                             "but solution can be less accurate)",
                        required=False)

    args = parser.parse_args()

    source_path = args.source
    replica_path = args.replica
    logs_path = args.logs
    interval = args.interval
    content_comparison_mode = False if args.comparison_mode == "metadata" else True

    logging.basicConfig(level=logging.NOTSET, handlers=[
        logging.FileHandler(logs_path),
        logging.StreamHandler(sys.stdout)
    ], format="%(asctime)s %(levelname)s %(message)s")

    while True:
        logging.info(msg=f"Start synchronization of replica folder: {replica_path} with source folder: {source_path}")
        logging.info(msg=f"Files comparison is performed based on files "
                         f"{'CONTENT' if content_comparison_mode else 'METADATA'}")
        start_time = time.time()
        synchronize_folders(source_path, replica_path, content_comparison_mode)
        execution_time = time.time() - start_time
        logging.info(msg=f"Synchronization completed in {execution_time}s")

        if execution_time < interval:
            time.sleep(interval - execution_time)
