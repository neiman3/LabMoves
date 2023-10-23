import os
import json
import pathlib
from src.excel import *
import shutil
import subprocess, platform


def get_config(project_root, configfilename='config.json'):
    # file format
    # - excelfile [workbook file name]
    configfile = os.path.join(project_root, configfilename)
    result = {
        "excelfile": None
    }
    if os.path.exists(configfile):
        # the config file exists
        f = open(configfile, )
        file = json.load(f)
        if "excelfile" in file:
            logging.debug("Loaded config file \"%s\"." % (configfilename))
            return file
        else:
            logging.error("Malformed config file. Please delete it and rerun the program.")
            raise RuntimeError
    else:
        logging.info("No config file exists.")
        i = 0
        while True:
            if i > 4:
                raise RuntimeError("Too many bad filenames")
            file = input("Path to excel file (existing or new) > ")
            if os.path.exists(os.path.dirname(file)):
                # ok- dir exists
                result["excelfile"] = file
                f = open(configfile, 'w')
                json.dump(result, f)
                logging.info("Created config file")
                if os.path.exists(file) and pathlib.Path(file).suffix in [".xlsx", ".xls"]:
                    # file already exists
                    break
                else:
                    # make a new file
                    wb = new_wb()
                    save_wb(file, wb)
                break
            print("Directory doesn't exist.")
            i += 1

        result['saveas'] = file_prompt("Please specify PDF save directory. >", True, 'dir')
        result['defaultimport'] = file_prompt("Please specify PDF save directory. >", True, 'dir')
        f = open(configfile, 'w')
        json.dump(result, f)
        f.close()

    return result


def file_prompt(text=" > ", must_exist=True, kind='file', max_retries=5, default=None, base_dir=None,
                auto_filetype=None):
    while True:
        i = 0
        if i > max_retries:
            print("Too many tries while entering file.")
            raise FileNotFoundError
        file = input(text)
        if base_dir is not None:
            file = os.path.join(base_dir, file)
        if auto_filetype is not None:
            # Automatically add the filetype if it is not present
            filetype = os.path.splitext(file)[1][1:]
            if not filetype.lower() == auto_filetype.lower():
                if filetype == '':
                    if auto_filetype[0] == '.':
                        # remove period
                        auto_filetype = auto_filetype[1:]
                    file += '.{}'.format(auto_filetype)
        if file == "":
            if default is not None:
                file = default
        if must_exist:
            if kind == 'file':
                if os.path.exists(file):
                    break
                else:
                    print("File {} does not exist.".format(file))
            else:
                if os.path.isdir(file):
                    break
                else:
                    print("Path {} does not exist or is not a directory.".format(file))
        else:
            break
        i += 1
    return file


def get_project_root():
    # returns root directory of the script
    result = os.getcwd()
    if os.path.isdir(os.path.join(result, '')):
        # in root folder
        return result
    else:
        result = os.path.dirname(result)
        return result


def copy_file(from_file, to_file):
    shutil.copy2(from_file, to_file)
    return


def delete_file(path):
    try:
        os.remove(path)
        logging.debug("Deleted file {}".format(path))
    except:
        logging.warning("Unable to remove file {} (is it open?)".format(path))
    return


def open_file_in_windows(filename):
    if platform.system() == "Darwin":
        subprocess.call(('open', filename))
    elif platform.system() == "Windows":
        os.startfile(filename)
    else:
        subprocess.call(('xdg-open', filename))
    return


def split_up(text: str, delimiters):
    for c in delimiters:
        text = text.replace(c, '\r')
    text = [i for i in text.split('\r') if i != '']
    return text


def user_edit(filename, message=None):
    # Prompt user to edit
    if message is None:
        print("Please fill out the excel template.")
    else:
        print(message)
    open_file_in_windows(filename)
    input("Press enter when you have saved and closed. [enter] ")


def add_dash_tag(filename, tag):
    # adds tag
    # example: /usr/bib/test.txt -> /usr/bib/test-tag.txt
    if '.' not in filename:
        return "{}-{}".format(filename, tag)
    return "-{}.".format(tag).join(filename.split('.'))
