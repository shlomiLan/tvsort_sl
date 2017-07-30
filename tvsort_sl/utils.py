# coding=utf-8
from __future__ import unicode_literals

import logging
import re
import traceback

import daiquiri as daiquiri
import requests
import winshell
import os

import yaml


def create_logger(log_path, log_name, log_level=logging.INFO):
    daiquiri.setup(level=log_level,
                   outputs=(daiquiri.output.File(directory=log_path, program_name=log_name), daiquiri.output.STDOUT,))
    return daiquiri.getLogger(program_name=log_name)


def is_compressed(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('COMPRESS_EXTS'))


def is_media(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('MEDIA_EXTS'))


def is_garbage_file(file_name, setting):
    return is_file_ext_in_list(get_file_ext(file_name), setting.get('GARBAGE_EXTS')) or 'sample' in file_name.lower()


def is_file_ext_in_list(file_ext, ext_list):
    return bool(file_ext in ext_list)


def get_file_ext(file_name):
    return file_name.split('.')[-1]


def get_file_name(file_path):
    return file_path.split('\\')[-1]


def get_folder_path_from_file_path(file_path):
    return '\\'.join(file_path.split('\\')[:-1])


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
        # retry to delete folder 10 times
        for retry in range(10):
            try:
                os.makedirs(folder_path)
                return True
            except Exception as e:
                logger.error(e)
                logger.error(traceback.print_exc())
                print('Folder deletion failed, retrying...')
        else:
            logger.error("Can't remove folder: {}".format(folder_path))
            return False

    return True


def delete_folder(folder_path, logger, force=False):
    try:
        if force:
            clean_folder(folder_path, logger)

        if folder_empty(folder_path):
            os.rmdir(folder_path)
            return True
        else:
            logger.error("Folder is not empty")
            return False
    except Exception as e:
        logger.error("Folder can't be deleted, Unexpected error: {}".format(e))
        return False


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
    string = re.sub(' ', '.', string)
    return '.'.join([str(x).capitalize() for x in string.split('.')])


def get_show_name(guess):
    return guess.get('title')


def remove_wrong_country_data(guess):
    if guess.get('title') == 'This is':
        guess['title'] += '.Us'
        if guess.get('country'):
            del guess['country']


def add_missing_country(guess, show_name):
    if show_name.lower() == 'house of cards':
        if not guess.get('country'):
            guess['country'] = 'US'


def create_file(file_path):
    dummy_file = open(file_path, str('w'))
    dummy_file.close()


def delete_file(file_path, logger, no_confirm=True):
    try:
        winshell.delete_file(file_path, no_confirm=no_confirm)
        return True
    except Exception as e:
        logger.error("Unexpected error: {}".format(e))
        return False


def copy_file(old_path, new_path, logger, move_file=True, no_confirm=True):
    # TODO: remove the 'new_file_path' parameter
    action = 'Moving' if move_file else 'Copying'
    logger.info('{} file: FROM {} TO {}'.format(action, old_path, new_path))

    try:
        if move_file:
            winshell.move_file(old_path, new_path, no_confirm=no_confirm)
        else:
            winshell.copy_file(old_path, new_path, no_confirm=no_confirm)
        return True
    except Exception as e:
        logger.error("Unexpected error: {}".format(e))
        return False


def folder_empty(folder_path):
    return not bool(get_files(folder_path))


def load_settings(is_test=False):
    configs = dict(PROJECT_NAME='tvsort_sl')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    settings_folder = '{}\{}\settings'.format(base_dir, configs.get('PROJECT_NAME'))
    conf_files = ['conf.yml', 'local.yml']
    if is_test:
        conf_files.append('test.yml')

    for file_name in conf_files:
        configs.update(yaml.load(open('{}\{}'.format(settings_folder, file_name))))

    return build_settings(base_dir, configs)


def update_xbmc(kodi_ip, logger):
    logger.info('Update XBMC')

    url = '{}/jsonrpc'.format(kodi_ip)
    data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
    return requests.post(url, json=data)


def build_settings(base_dir, configs):
    # This should be overwrite by prod OR test settings
    configs['TV_PATH']       = '{}\\TVShows'.format(configs['BASE_DRIVE'])
    configs['MOVIES_PATH']   = '{}\\Movies'.format(configs['BASE_DRIVE'])
    configs['UNSORTED_PATH'] = '{}\\Unsortted'.format(configs['BASE_DRIVE'])
    configs['DUMMY_PATH']    = '{}\\Dummy'.format(configs['BASE_DRIVE'])
    configs['LOG_PATH']      = '{}\\logs'.format(base_dir)

    configs['TEST_FILES']    = '{}\\tvsort_sl\\test_files'.format(base_dir)
    # This folder should have any files init
    configs['FAKE_PATH']     = '{}\\xxx'.format(configs['BASE_DRIVE'])

    configs['DUMMY_FILE_PATH']      = '{}\{}'.format(configs['TV_PATH'], configs['DUMMY_FILE_NAME'])
    configs['TEST_FILE_PATH']       = '{}\{}'.format(configs['UNSORTED_PATH'], 'test.txt')
    configs['TEST_FILE_PATH_IN_TV'] = '{}\{}'.format(configs['TV_PATH'], 'test.txt')

    # test files
    configs['TEST_ZIP_NAME'] = 'zip_test.zip'
    configs['TEST_TV_NAME']  = 'Mr.Robot.S01E01.720p.BluRay.x264.ShAaNiG.mkv'

    return configs
