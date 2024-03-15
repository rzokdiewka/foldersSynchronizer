import argparse
import logging
import os
import shutil
import sys


def exist_but_modified(source_path: str, replica_path: str) -> None:
    logging.info(f"{replica_path} was modified. Copying source and replacing in replica folder.")
    if os.path.isfile(source_path):
        shutil.copy2(source_path, replica_path)
    elif os.path.isdir(source_path):
        synchronize_folder(source_path, replica_path)


def synchronize_folder(source_path: str, replica_path: str) -> None:
    if not os.path.exists(replica_path):
        # if replica folder doesn't exist
        logging.info(
            f"Replica PATH {replica_path} doesn't exist. Creating one and copying source path content into it.")
        shutil.copytree(source_path, replica_path)
    else:
        # if replica folder exist then iterate over files/folders in source path
        print("source files", os.listdir(source_path))
        for f in os.listdir(source_path):
            # f can be a file or folder
            print(f)
            source_f = f"{source_path}/{f}"
            replica_f = f"{replica_path}/{f}"
            print(os.stat(source_f))
            print(os.stat(replica_f))
            if f.startswith('.'):
                logging.warning(f"{source_f} is hidden and can't be synchronized.")
                continue

            if os.path.isfile(source_f):

                if not os.path.exists(replica_f):
                    # if file doesn't exist
                    logging.info(f"Replica FILE {replica_f} doesn't exist. Copying source FILE into replica path.")
                    shutil.copy2(source_f, replica_f)
                elif os.path.getmtime(source_f) != os.path.getmtime(replica_f):  # todo size??
                    # if file was modified
                    logging.info(f"Replica FILE {replica_f} was modified. Replacing it with source FILE.")
                    shutil.copy2(source_f, replica_f)

            elif os.path.isdir(source_f):
                synchronize_folder(source_f, replica_f)

        # if files or folders aren't in source path
        for f in os.listdir(replica_path):
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
    parser.add_argument("-s", "--source", help="path to source folder")
    parser.add_argument("-r", "--replica", help="path to source folder")
    parser.add_argument("-l", "--logs", help="path log file")

    parser.add_argument("-i", "--interval", help="synchronization interval [s], 3600 by default", default=3600,
                        required=False)

    args = parser.parse_args()

    source_path = args.source
    replica_path = args.replica
    logs_path = args.logs
    interval = args.interval

    logging.basicConfig(level=logging.NOTSET, handlers=[
        logging.FileHandler(logs_path),
        logging.StreamHandler(sys.stdout)
    ], format="%(asctime)s %(levelname)s %(message)s")  # , datefmt="%Y-%m-%d %H:%M:%S")
    logging.info(msg=f"Start synchronization of replica folder: {replica_path} with source folder: {source_path}")

    synchronize_folder(source_path, replica_path)
