import json
import logging
from datetime import datetime


def json_write_to_file(j_str, filename):
    """
    :param j_str: json string
    :param filename: json file to save
    :return: True - if saved. None - if error
    """

    try:
        with open(filename, 'w', encoding="utf-8") as file:
            json.dump(j_str, file, indent=4, ensure_ascii=False)
            return True
    except Exception as e:
        print(f'[!] Error <json_write_to_file> writing to {filename}: {e}')
        return None


def json_read_to_obj(filename) -> dict | str:
    """
    There are 2 ways to read JSON from file:
    1. Read file to a string - then string to JSON: "json.loads()" - deserialize string
    2. Read file directly to JSON: "json.load()" - deserialize a file itself, it accepts a file object
    :param filename: json file
    :return: json obj if OK. str - string with error
    """
    try:
        with open(filename, 'r', encoding="UTF-8") as file:
            json_obj = json.load(file)
        file.close()
        return json_obj
    except Exception as e:
        return f'[json_read_to_obj]: Exception reading {filename}: {e}'


def file_read_to_list(the_file):
    """
    :param the_file: input file
    :return: list if read ok. None - if error
    """
    try:
        tmp_file = open(the_file, 'r',  encoding="utf-8")
        the_list = tmp_file.read().splitlines()     # Create list
        tmp_file.close()
        return the_list
    except OSError as e:
        print(f'[!] Error <file_read_to_list>: {e}')
        return None


# DateTime
def get_timeprint():
    # now = datetime.now()  # current date and time
    #
    # year = now.strftime("%Y")
    # print("year:", year)
    #
    # month = now.strftime("%m")
    # print("month:", month)
    #
    # day = now.strftime("%d")
    # print("day:", day)
    #
    # time = now.strftime("%H:%M:%S")
    # print("time:", time)
    #
    # date_time = now.strftime("%m/%d/%Y, %H:%M:%S")
    # print("date and time:", date_time)
    return datetime.now().strftime("%d_%m_%Y_%H_%M_%S")


# DateTime
def get_str_timeprint():
    """
    Suitable only for console/log print
    Not suitable for filenames (since contains ':' '/' symbol)
    :return:
    """
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def init_log(log_file_name, log_path, log_alias) -> logging.Logger | str:
    """

    :param log_file_name:
    :param log_path:
    :param log_alias:
    :return: Logger OBJ - if OK / str - string with error
    """
    try:
        log = logging.getLogger(log_alias)
        log.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler(f'{log_path}/{log_file_name}', encoding='utf-8')
        formatter = logging.Formatter('[%(asctime)s : %(levelname)s : %(name)s ]:  %(message)s')
        file_handler.setFormatter(formatter)
        log.addHandler(file_handler)
        return log
    except Exception as e:
        return f'[init_log]: Exception: Can not create log. ErrMsg: {e}'
