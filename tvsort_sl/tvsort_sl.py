# coding=utf-8
from __future__ import unicode_literals

import traceback

import re
import requests

import winshell
from guessit import guessit
from opster import command
import os
import patoolib
import logging
from conf import SortSettings

settings = SortSettings()


def is_compressed(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.COMPRESS_EXTS)


def is_media(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.MEDIA_EXTS)


def is_garbage_file(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.GARBAGE_EXTS) or 'sample' in file_name.lower()


def is_file_ext_in_list(file_ext, ext_list):
    return bool(file_ext in ext_list)


def get_file_ext(file_name):
    return file_name.split('.')[-1]


def get_file_name(file_path):
    return file_path.split('\\')[-1]


def get_folder_name(file_path):
    return '\\'.join(file_path.split('\\')[:-1])


def get_files(path):
    files = []

    for root, dirs, walk_files in os.walk(path):
        for f in walk_files:
            files.append(os.path.join(root, f))
    
    return sorted(files)


def is_tv_show(guess):
    return bool(guess.get('episode'))


def is_movie(guess):
    return guess.get('type') == 'movie'


def is_file_exists(file_path):
    return os.path.isfile(file_path)


def is_folder_exists(file_path):
    return os.path.isdir(file_path)


def create_folder(folder_path):
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)


def delete_folder(folder_path, logger=None):
    try:
        if folder_empty(folder_path):
            os.rmdir(folder_path)
            return True
        else:
            if logger:
                logger.error("Folder is not empty")
            return False
    except Exception as e:
        if logger:
            logger.error("Folder can't be deleted, Unexpected error: {}".format(e))
        return False


def create_logger():
    logger = logging.getLogger('tvshow')
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler())
    logger.addHandler(logging.FileHandler(filename=settings.LOG_FILE_PATH))

    return logger


def is_process_already_run(file_path):
    return is_file_exists(file_path)


def transform_to_path_name(string):
    if isinstance(string, int):
        string = str(string)
    string = re.sub(' ', '.', string)
    return '.'.join([str(x).capitalize() for x in string.split('.')])


def get_show_name(guess):
    show_name = guess.get('title')
    if show_name == 'This.Is':
        show_name += '.Us'
        if guess.get('country'):
            del guess['country']

    return show_name


def add_missing_country(guess, show_name):
    if show_name.lower() == 'house of cards':
        if not guess.get('country'):
            guess['country'] = 'US'


def create_file(file_path):
    dummy_file = open(file_path, str('w'))
    dummy_file.close()


def delete_file(file_path, logger=None, no_confirm=True):
    try:
        winshell.delete_file(file_path, no_confirm=no_confirm)
        return True
    except Exception as e:
        if logger:
            logger.error("Unexpected error: {}".format(e))
        return False


def copy_file(old_path, new_path, new_file_path, logger=None, move_file=True, no_confirm=True):
    if logger:
        action = 'Moving' if move_file else 'Copying'
        logger.info('{} file: FROM {} TO {}'.format(action, old_path, new_file_path))

    try:
        if move_file:
            winshell.move_file(old_path, new_path, no_confirm=no_confirm)
        else:
            winshell.copy_file(old_path, new_path, no_confirm=no_confirm)
        return True
    except Exception as e:
        if logger:
            logger.error("Unexpected error: {}".format(e))
        return False


def folder_empty(folder_path):
    return not bool(get_files(folder_path))


@command()
def main():
    logger = create_logger()
    path = settings.UNSORTED_PATH
    dummy_file_path = settings.DUMMY_FILE_PATH

    if not is_process_already_run(dummy_file_path):
        try:
            create_file(dummy_file_path)

            for file_path in get_files(path):
                if is_compressed(file_path):
                    logger.info("Extracting {}".format(file_path))
                    patoolib.extract_archive(file_path, outdir=path)
                    delete_file(file_path, logger=logger)

            for file_path in get_files(path):
                logger.info('Checking file: {}'.format(file_path))

                if is_garbage_file(file_path):
                    logger.info('Removing file: {}'.format(file_path))
                    delete_file(file_path, logger=logger)
                elif is_media(file_path):
                    guess = guessit(file_path)
                    new_path = None
                    if is_tv_show(guess):
                        base = settings.TV_PATH
                        show_name = transform_to_path_name(get_show_name(guess))
                        add_missing_country(guess, show_name)
                        if guess.get('country'):
                            show_name += '.{}'.format(guess.get('country'))
                        create_folder(show_name)
                        new_path = '{}\{}'.format(base, show_name)

                    elif is_movie(guess):
                        new_path = settings.MOVIES_PATH

                    new_file_path = '{}\{}'.format(new_path, get_file_name(file_path))
                    copy_file(file_path, new_path, new_file_path, logger, move_file=settings.MOVE_FILES)

                folder_path = get_folder_name(file_path)
                if folder_empty(folder_path):
                    os.rmdir(folder_path)

            # Update XBMC
            logger.info('Update XBMC')

            url = '{}/jsonrpc'.format(settings.KODI_IP)
            data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
            requests.post(url, json=data)

        except Exception as e:
            logger.error(e)
            logger.error(traceback.print_exc())

        finally:
            delete_file(dummy_file_path, logger=logger)
    else:
        logger.info('Proses already running')


if __name__ == "__main__":
    main()
