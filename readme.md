## DirC

This is a python script used to delete files or directories found inside a specific set of directories.
The configuration 

## Requirements

- Python version supported : 3.7 or later
- A configuration file `settings.json` located in the same directory as the script.
- A JSON file containing a collection of directories to inspect.

### About configuration file

**The configuration file is named `settings.json` and must be located in the same directory as the script `main.py`.**

The file should contain two mandatory keys:

1. `db_for_cleaning`: string

    It's the full path of the file witch contain the list of directories to inspect.
   The file referred **must be a JSON file** containing a collection of directories.
   An example of the file is illustrated in `dirs.json.example`


2. `log_file`: string
    
    Once a directory content is deleted from the system, some details about the deleted files are reported.
This is the **full path of log file** location. The **file must be a `csv` file**. 
You can specify an existing csv file path, or specify the desired location for the log file if it doesn't exist yet. 
Make sure the path you specify has the required OS permission for reading and writing.
If the file does not exist yet, the program will create it automotically and then start using it.
Simply make sure to provide a value for this key.


Credits: 

- Github: `david95thinkcode`
- Email: `david95thinkcode@gmail.com`