import os
import shutil
from typing import List, Optional, Tuple, Dict, Union

import requests


def is_compressed(file_name: str, extensions: Dict[str, List[str]]) -> bool:
    return is_file_ext_in_list(get_file_ext(file_name), extensions.get('COMPRESS', []))


def is_garbage_file(file_name: str, extensions: Dict[str, List[str]]) -> bool:
    return (
        is_file_ext_in_list(get_file_ext(file_name), extensions.get('GARBAGE', []))
        or 'sample' in file_name.lower()
    )


def is_file_ext_in_list(file_ext: str, ext_list: List[str]) -> bool:
    return bool(file_ext.lower() in ext_list)


def get_file_ext(file_name: str) -> str:
    return file_name.split('.')[-1]


def get_file_name(file_path: str) -> str:
    return file_path.split(os.sep)[-1]


def get_folder_path_from_file_path(file_path: str) -> str:
    return os.path.dirname(file_path)


def get_files(path: str) -> List[str]:
    files = []

    for root, _, walk_files in os.walk(path):
        for f in walk_files:
            files.append(os.path.join(root, f))

    return sorted(files)


def get_folders(path: str) -> List[str]:
    folders = []

    for root, dirs, _ in os.walk(path):
        for d in dirs:
            folders.append(os.path.join(root, d))

    return sorted(folders)


def is_tv_show(guess: dict) -> bool:
    return bool(guess.get('episode') is not None)


def is_movie(guess: dict) -> bool:
    return guess.get('type') == 'movie'


def is_file_exists(file_path: str) -> bool:
    return os.path.isfile(file_path)


def is_folder_exists(file_path: str) -> bool:
    return os.path.isdir(file_path)


def create_folder(folder_path: str) -> Optional[List[Tuple[str, str]]]:
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        return [('info', f'Creating folder: {folder_path}')]

    return None


def delete_folder(folder_path: str, force: bool = False) -> List[Tuple[str, str]]:
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


def delete_folder_if_empty(folder_path: str) -> List[Tuple[str, str]]:
    if folder_empty(folder_path):
        return delete_folder(folder_path)

    return [('', '')]


def clean_folder(folder_path: str) -> List[Tuple[str, str]]:
    msseages = []
    for file_path in get_files(folder_path):
        msseages.extend(delete_file(file_path))

    for sub_folder in get_folders(folder_path):
        msseages.extend(delete_folder(sub_folder))

    return msseages


def is_process_already_running(file_path: str) -> bool:
    return is_file_exists(file_path)


def transform_to_path_name(string: Union[str, int]) -> str:
    if isinstance(string, int):
        string = str(string)
    string = string.replace(' ', '.')
    return '.'.join([str(x).capitalize() for x in string.split('.')])


def get_show_name(video: Dict[str, str]) -> Optional[str]:
    return video.get('title')


def add_missing_country(video: dict, show_name: str) -> None:
    if show_name.lower() == 'house.of.cards':
        if not video.get('country'):
            video['country'] = 'US'


def create_file(file_path: str) -> List[Tuple[str, str]]:
    dummy_file = open(file_path, str('w'))
    dummy_file.close()
    return [('info', f'File was created, in: {file_path}')]


def delete_file(file_path: str) -> List[Tuple[str, str]]:
    try:
        os.remove(file_path)
        return [('info', f'Removing file: {file_path}')]
    except Exception as e:
        return [('error', f'Unexpected error: {e}')]


def copy_file(
    old_path: str, new_path: str, move_file: bool = True
) -> List[Tuple[str, str]]:
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


def folder_empty(folder_path: str) -> bool:
    return not bool(get_files(folder_path))


def update_xbmc(kodi_ip: str) -> List[Tuple[str, str]]:
    url = '{}/jsonrpc'.format(kodi_ip)
    data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
    response = requests.post(url, json=data)
    if response.status_code == 200:
        return [('info', 'Update XBMC successfully')]

    return [('error', 'Invalid response: {}'.format(response))]


def check_project_setup(settings, conf_files):
    log_folder_path = settings.get('LOG_PATH')

    # Logs folder exists
    if not is_folder_exists(log_folder_path):
        return [('error', f'Logs folder is missing, should be at: {log_folder_path}')]

    # Configs files exists
    for file_path in conf_files:
        if not is_file_exists(file_path):
            return [
                (
                    'error',
                    'Missing config file, you must have local.yml and test.yml in settings folder. '
                    'Use files in settings/templates for reference',
                )
            ]

    return [('info', 'Project setup successfully')]
