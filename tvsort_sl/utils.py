# coding=utf-8
from __future__ import unicode_literals

import requests
import os

import shutil


def is_compressed(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('COMPRESS_EXTS'))


def is_media(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('MEDIA_EXTS'))


def is_garbage_file(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('GARBAGE_EXTS')) or 'sample' in file_name.lower()


def is_file_ext_in_list(file_ext, ext_list):
    return bool(file_ext.lower() in ext_list)


def get_file_ext(file_name):
    return file_name.split('.')[-1]


def get_file_name(file_path):
    return file_path.split('\\')[-1]


def get_folder_path_from_file_path(file_path):
    return os.path.dirname(file_path)


def get_files(path):
    files = []

    for root, _, walk_files in os.walk(path):
        for f in walk_files:
            files.append(os.path.join(root, f))

    return sorted(files)


def get_folders(path):
    folders = []

    for root, dirs, _ in os.walk(path):
        for d in dirs:
            folders.append(os.path.join(root, d))

    return sorted(folders)


def is_tv_show(guess):
    return bool(guess.get('episode'))


def is_movie(guess):
    return guess.get('type') == 'movie'


def is_file_exists(file_path):
    return os.path.isfile(file_path)


def is_folder_exists(file_path):
    return os.path.isdir(file_path)


def create_folder(folder_path, logger):
    if not os.path.exists(folder_path):
        logger.info('Creating folder: {}'.format(folder_path))
        os.makedirs(folder_path)

    return True


def delete_folder(folder_path, logger, force=False):
    try:
        if force:
            logger.info('Cleaning folder: {}'.format(folder_path))
            clean_folder(folder_path, logger)

        if folder_empty(folder_path):
            logger.info('Deleting folder: {}'.format(folder_path))
            os.rmdir(folder_path)
            return True
        else:
            logger.error("Folder is not empty")
            return False
    except Exception as e:
        logger.error("Folder can't be deleted, Unexpected error: {}".format(e))
        return False


def delete_folder_if_empty(folder_path, logger):
    if folder_empty(folder_path):
        delete_folder(folder_path, logger)


def clean_folder(folder_path, logger):
    for file_path in get_files(folder_path):
        delete_file(file_path, logger)

    for sub_folder in get_folders(folder_path):
        delete_folder(sub_folder, logger)


def is_process_already_running(file_path):
    return is_file_exists(file_path)


def transform_to_path_name(string):
    if isinstance(string, int):
        string = str(string)
    string = string.replace(' ', '.')
    return '.'.join([str(x).capitalize() for x in string.split('.')])


def get_show_name(guess):
    return guess.get('title')


def remove_wrong_country_data(guess):
    if guess.get('title') == 'This is':
        guess['title'] += '.Us'
        if guess.get('country'):
            del guess['country']


def add_missing_country(guess, show_name):
    if show_name.lower() == 'house.of.cards':
        if not guess.get('country'):
            guess['country'] = 'US'


def create_file(file_path):
    dummy_file = open(file_path, str('w'))
    dummy_file.close()


def delete_file(file_path, logger):
    try:
        os.remove(file_path)
        return True
    except Exception as e:
        logger.error("Unexpected error: {}".format(e))
        return False


def copy_file(old_path, new_path, logger, move_file=True):
    action = 'Moving' if move_file else 'Copying'
    logger.info('{} file: FROM {} TO {}'.format(action, old_path, new_path))

    try:
        if move_file:
            shutil.move(old_path, new_path)
        else:
            shutil.copy(old_path, new_path)
        return True
    except Exception as e:
        logger.error("Unexpected error: {}".format(e))
        return False


def folder_empty(folder_path):
    return not bool(get_files(folder_path))


def update_xbmc(kodi_ip, logger):
    logger.info('Update XBMC')

    url = '{}/jsonrpc'.format(kodi_ip)
    data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
    return requests.post(url, json=data)
