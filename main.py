import argparse
import logging
import os
import shutil
import sys
import time


def synchronize_folders(source_path: str, replica_path: str) -> None:
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
                if not os.path.exists(replica_f):
                    # if file doesn't exist
                    logging.info(f"Replica FILE {replica_f} doesn't exist. Copying source FILE into replica path.")
                    shutil.copy2(source_f, replica_f)
                elif os.path.getmtime(source_f) != os.path.getmtime(replica_f) or os.path.getsize(
                        source_f) != os.path.getsize(replica_f):
                    # if file was modified
                    logging.info(f"Replica FILE {replica_f} was modified. Replacing it with source FILE.")
                    shutil.copy2(source_f, replica_f)

            elif os.path.isdir(source_f):
                synchronize_folders(source_f, replica_f)

        # if files or folders aren't in source path
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


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description="Program that synchronizes two folders: source and replica. Requires to pass arguments.")
    parser.add_argument("-s", "--source", help="(required) path to source folder", required=True)
    parser.add_argument("-r", "--replica", help="(required) path to source folder", required=True)
    parser.add_argument("-l", "--logs", help="(required) path log file", required=True)

    parser.add_argument("-i", "--interval", help="(optional) synchronization interval [s], 3600 by default", default=3600,
                        required=False, type=int)

    args = parser.parse_args()

    source_path = args.source
    replica_path = args.replica
    logs_path = args.logs
    interval = args.interval

    logging.basicConfig(level=logging.NOTSET, handlers=[
        logging.FileHandler(logs_path),
        logging.StreamHandler(sys.stdout)
    ], format="%(asctime)s %(levelname)s %(message)s")

    while True:
        logging.info(msg=f"Start synchronization of replica folder: {replica_path} with source folder: {source_path}")
        start_time = time.time()
        synchronize_folders(source_path, replica_path)
        execution_time = time.time() - start_time
        if execution_time < interval:
            time.sleep(interval - execution_time)
