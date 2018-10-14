# coding: future_fstrings

import os
import shutil
from typing import List, Optional, Tuple, Dict, Union

import requests


def is_compressed(file_name, extensions):
    return is_file_ext_in_list(get_file_ext(file_name), extensions.get('COMPRESS', []))
is_compressed.__annotations__ = {'file_name': str, 'extensions': Dict[str, List[str]], 'return': bool}

def is_garbage_file(file_name, extensions):
    return is_file_ext_in_list(get_file_ext(file_name), extensions.get('GARBAGE', [])) or 'sample' in file_name.lower()
is_garbage_file.__annotations__ = {'file_name': str, 'extensions': Dict[str, List[str]], 'return': bool}

def is_file_ext_in_list(file_ext, ext_list):
    return bool(file_ext.lower() in ext_list)
is_file_ext_in_list.__annotations__ = {'file_ext': str, 'ext_list': List[str], 'return': bool}

def get_file_ext(file_name):
    return file_name.split('.')[-1]
get_file_ext.__annotations__ = {'file_name': str, 'return': str}

def get_file_name(file_path):
    return file_path.split(os.sep)[-1]
get_file_name.__annotations__ = {'file_path': str, 'return': str}

def get_folder_path_from_file_path(file_path):
    return os.path.dirname(file_path)
get_folder_path_from_file_path.__annotations__ = {'file_path': str, 'return': str}

def get_files(path):
    files = []

    for root, _, walk_files in os.walk(path):
        for f in walk_files:
            files.append(os.path.join(root, f))

    return sorted(files)
get_files.__annotations__ = {'path': str, 'return': List[str]}

def get_folders(path):
    folders = []

    for root, dirs, _ in os.walk(path):
        for d in dirs:
            folders.append(os.path.join(root, d))

    return sorted(folders)
get_folders.__annotations__ = {'path': str, 'return': List[str]}

def is_tv_show(guess):
    return bool(guess.get('episode'))
is_tv_show.__annotations__ = {'guess': dict, 'return': bool}

def is_movie(guess):
    return guess.get('type') == 'movie'
is_movie.__annotations__ = {'guess': dict, 'return': bool}

def is_file_exists(file_path):
    return os.path.isfile(file_path)
is_file_exists.__annotations__ = {'file_path': str, 'return': bool}

def is_folder_exists(file_path):
    return os.path.isdir(file_path)
is_folder_exists.__annotations__ = {'file_path': str, 'return': bool}

def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return [('info', f'Creating folder: {folder_path}')]

    return None
create_folder.__annotations__ = {'folder_path': str, 'return': Optional[List[Tuple[str, str]]]}

def delete_folder(folder_path, force=False):
    try:
        messages = []
        if force:
            messages.append(('info', f'Cleaning folder: {folder_path}'))
            messages.extend(clean_folder(folder_path))

        if folder_empty(folder_path):
            messages.append(('info', 'Deleting folder: {}'.format(folder_path)))
            os.rmdir(folder_path)
            return messages
        else:
            return [('error', 'Folder is not empty')]
    except Exception as e:
        return [('error', f"Folder can't be deleted, Unexpected error: {e}")]
delete_folder.__annotations__ = {'folder_path': str, 'force': bool, 'return': List[Tuple[str, str]]}

def delete_folder_if_empty(folder_path):
    if folder_empty(folder_path):
        return delete_folder(folder_path)

    return [('', '')]
delete_folder_if_empty.__annotations__ = {'folder_path': str, 'return': List[Tuple[str, str]]}

def clean_folder(folder_path):
    msseages = []
    for file_path in get_files(folder_path):
        msseages.extend(delete_file(file_path))

    for sub_folder in get_folders(folder_path):
        msseages.extend(delete_folder(sub_folder))

    return msseages
clean_folder.__annotations__ = {'folder_path': str, 'return': List[Tuple[str, str]]}

def is_process_already_running(file_path):
    return is_file_exists(file_path)
is_process_already_running.__annotations__ = {'file_path': str, 'return': bool}

def transform_to_path_name(string):
    if isinstance(string, int):
        string = str(string)
    string = string.replace(' ', '.')
    return '.'.join([str(x).capitalize() for x in string.split('.')])
transform_to_path_name.__annotations__ = {'string': Union[str, int], 'return': str}

def get_show_name(video):
    return video.get('title')
get_show_name.__annotations__ = {'video': Dict[str, str], 'return': Optional[str]}

def add_missing_country(video, show_name):
    if show_name.lower() == 'house.of.cards':
        if not video.get('country'):
            video['country'] = 'US'
add_missing_country.__annotations__ = {'video': dict, 'show_name': str, 'return': None}

def create_file(file_path):
    dummy_file = open(file_path, str('w'))
    dummy_file.close()
    return [('info', f'File was created, in: {file_path}')]
create_file.__annotations__ = {'file_path': str, 'return': List[Tuple[str, str]]}

def delete_file(file_path):
    try:
        os.remove(file_path)
        return [('info', f'Removing file: {file_path}')]
    except Exception as e:
        return [('error', f'Unexpected error: {e}')]
delete_file.__annotations__ = {'file_path': str, 'return': List[Tuple[str, str]]}

def copy_file(old_path, new_path, move_file=True):
    action = 'Moving' if move_file else 'Copying'

    try:
        if move_file:
            shutil.move(old_path, new_path)
        else:
            shutil.copy(old_path, new_path)
        return [('info', f'{action} file: FROM {old_path} TO {new_path}')]
    except Exception as e:
        # If error because file already in new path delete the old file
        if 'already exists' in str(e):
            messages = [('error', str(e))]
            messages.extend(delete_file(old_path))
            return messages
        else:
            return [('error', f'Unexpected error: {e}')]
delete_folder.__annotations__ = {'old_path': str, 'new_path': str, 'move_file': bool, 'return': List[Tuple[str, str]]}

def folder_empty(folder_path):
    return not bool(get_files(folder_path))
delete_folder.__annotations__ = {'older_path': str, 'return': bool}

def update_xbmc(kodi_ip):
    url = '{}/jsonrpc'.format(kodi_ip)
    data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
    requests.post(url, json=data)
    return [('info', 'Update XBMC successfully')]
delete_folder.__annotations__ = {'kodi_ip': str, 'return': List[Tuple[str, str]]}

def check_project_setup(settings, conf_files):
    log_folder_path = settings.get('LOG_PATH')

    # Logs folder exists
    if not is_folder_exists(log_folder_path):
        return [('error', f'Logs folder is missing, should be at: {log_folder_path}')]

    # Configs files exists
    for file_path in conf_files:
        if not is_file_exists(file_path):
            return [('error', 'Missing config file, you must have local.yml and test.yml in settings folder. '
                              'Use files in settings/templates for reference')]

    return [('info', 'Project setup successfully')]
