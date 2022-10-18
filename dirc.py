from datetime import datetime
import shutil
import json
import csv
import os


class DeletedFile:
    path: str
    size: int
    is_file: bool
    is_directory: bool
    time: str

    def __init__(self, path: str, size: int, is_file: bool, is_folder: bool):
        self.path = path
        self.size = size
        self.is_file = is_file
        self.is_directory = is_folder

    def to_array(self) -> [str]:
        return [
            self.time,
            self.path,
            self.size,
            self.is_file,
            self.is_directory
        ]


class Cdirectory:
    path: str
    expiry_in_minutes: int = 0
    cleaning_type: str

    def __init__(self, path, expiry_minutes: int, type: str):
        self.path = path
        self.expiry_in_minutes = expiry_minutes
        self.cleaning_type = type


class Setting:
    db_location: str
    log_file_location: str

    def __init__(self, db_location_on_disk: str):
        self.set_db_location(db_location_on_disk)

    def set_db_location(self, db_location_on_disk):
        with open(db_location_on_disk, "r") as read_setting:
            settings_json = json.load(read_setting)

        if type(settings_json['db_for_cleaning']) is str:
            self.db_location = settings_json['db_for_cleaning']
        else:
            print("Missing db path")

        if type(settings_json['log_file']) is str:
            self.log_file_location = settings_json['log_file']
        else:
            print("Missing log file in settings file")


def is_old_file(file_path: str, expiry_limit: int) -> bool:
    # A file is too old when :
    # current_time - last_modified_date >= expiry_limit

    today_datetime = datetime.now()
    last_modified = os.path.getctime(file_path)
    parsed_last_modified = datetime.fromtimestamp(last_modified)
    diff = today_datetime - parsed_last_modified
    diff_min = round(diff.total_seconds() / 60)
    response = diff_min >= expiry_limit

    return response


def report_deletion(deleted_files: list[DeletedFile]) -> None:
    rows = []
    for e in deleted_files:
        rows.append(e.to_array())

    if global_setting.log_file_location != '':
        try:
            with open(global_setting.log_file_location, 'a+', encoding='UTF8') as file:
                writer = csv.writer(file)
                writer.writerows(rows)
        except FileNotFoundError:
            print("FileNotFoundError! Can't write in log file at:", global_setting.log_file_location)
        except:
            print("Error! Something went wrong during writing in log file.")


def clean_directory(c_directory: Cdirectory) -> None:
    # Get list of files/directories found inside the Directory
    # Delete them Directory allows :
    # - f for file deletion
    # - d for directory deletion
    # - fd/df for files and directories deletion
    files_in_dir = os.listdir(c_directory.path)
    can_delete_files = 'f' in c_directory.cleaning_type
    can_delete_dirs = 'd' in c_directory.cleaning_type
    deletion_list = []
    for file in files_in_dir:
        file_path = c_directory.path + "/" + file  # Building file path
        is_deletable = is_old_file(file_path, c_directory.expiry_in_minutes)
        if is_deletable:
            is_deleted = True
            df = DeletedFile(file_path, os.path.getsize(file_path),
                             os.path.isfile(file_path),
                             os.path.isdir(file_path))
            if os.path.isfile(file_path) & can_delete_files:
                os.remove(file_path)  # Delete the file
                pass
            elif os.path.isdir(file_path) & can_delete_dirs:
                shutil.rmtree(file_path)  # Delete dir and subtree
                pass
            else:
                is_deleted = False
                pass
            df.time = datetime.now()  # Update time
            if is_deleted:
                deletion_list.append(df)
    report_deletion(deletion_list)


def get_directories_list() -> list[Cdirectory]:
    c_directories = []
    if (global_setting.db_location != '') & (os.path.exists(global_setting.db_location)):
        print("* Directories DB found")
        try:
            with open(global_setting.db_location, 'r') as reading:
                directories = json.load(reading)
            for d in directories:
                if os.path.lexists(d['path']) & os.path.isdir(d['path']):
                    c_directory = Cdirectory(d['path'], d['expiry'], d['type'])
                    c_directories.append(c_directory)
                    print("** Found directory:", c_directory.path)
                else:
                    print("** Skipping directory: ", d['path'])
        except FileNotFoundError:
            print("FileNotFoundError. Failed to find db location at:", global_setting.db_location)
        except:
            print("Error! Something went wrong during writing in log file.")
    else:
        print("* Directories DB not found!")

    return c_directories


def start() -> None:
    c_directories = get_directories_list()
    print("** Directories count:", len(c_directories))

    if len(c_directories) > 0:
        for cd in c_directories:
            clean_directory(cd)

    print("Bye Bye!")


def get_settings() -> Setting:
    settings_file_path = "settings.json"
    settings: Setting = None
    if not os.path.lexists(settings_file_path):
        print("* FileNotFoundError: Failed to find settings file located at: " + settings_file_path)
    else:
        settings = Setting(settings_file_path)
        print("* Configuration file found")

    return settings


global_setting: Setting
# Main method
if __name__ == '__main__':
    print("**************************")
    print("* DirC: Directory Cleaner")
    print("**************************\n")
    try:
        global_setting = get_settings()
        start()
    except:
        print("Error: Something went wrong!")
