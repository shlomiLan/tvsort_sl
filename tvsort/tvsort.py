import traceback

import re
import requests

import winshell
from guessit import guessit
from opster import command
import os
import patoolib
import logging

from conf import settings


def is_compressed(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.compress_exts)


def is_media(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.media_exts)


def is_garbage_file(file_name):
    return is_file_ext_in_list(get_file_ext(file_name), settings.garbage_exts)


def is_file_ext_in_list(file_ext, ext_list):
    return bool(file_ext in ext_list)


def get_file_ext(file_name):
    return file_name.split('.')[-1]


def get_files(path):
    files = []

    for root, dirs, walk_files in os.walk(path):
        for f in walk_files:
            f_path = os.path.join(root, f)
            if "sample" in f_path.lower():
                continue
            else:
                files.append(f)
    
    return sorted(files)


def is_tv_show(guess):
    return bool(guess.get('episode'))


def is_movie(guess):
    return guess.get('type') == 'movie'


def is_file_exists(file_path):
    return os.path.isfile(file_path)


def create_folder(show_name, base_path=settings.BASE_DIR):
    new_dir_path = '{}\{}'.format(base_path, show_name)
    if not os.path.exists(new_dir_path):
        os.makedirs(new_dir_path)


def create_logger():
    logger = logging.getLogger('tvshow')
    logger.level = logging.DEBUG
    logger.addHandler(logging.StreamHandler())
    create_folder('log')
    logger.addHandler(logging.FileHandler(filename=settings.log_path))

    return logger


# TODO: improve this logic
def remove_file(file_path):
    try:
        os.remove(file_path)
    except:
        return False

    return True


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


def create_dummy_file(dummy_file_path):
    dummy_file = open(dummy_file_path, 'w')
    dummy_file.close()


def delete_dummy_file(dummy_file_path):
    remove_file(dummy_file_path)


@command()
def main():
    logger = create_logger()
    path = settings.unsorted_path
    dummy_file_path = settings.dummy_file_path

    # TODO: improve this logic
    if not is_process_already_run(dummy_file_path):
        create_dummy_file(dummy_file_path)

        for file_name in get_files(path):
            if is_compressed(file_name):
                # TODO: fix this part
                logger.info("Extracting {}".format(file_name))
                patoolib.extract_archive(file_name, outdir=path)
                remove_file(file_name)

        for file_name in get_files(path):
            logger.info('Checking file: {}'.format(file_name))
            file_path = '{}\{}'.format(path, file_name)

            try:
                if is_media(file_name):
                    guess = guessit(file_name)
                    new_path = None
                    if is_tv_show(guess):
                        base = settings.tv_path
                        # TODO: fix 'this is us' and 'Shameless' logic
                        show_name = get_show_name(guess)
                        if guess.get('country'):
                            show_name += '.{}'.format(guess.get('country'))
                        show_name = transform_to_path_name(show_name)
                        create_folder(show_name, base)
                        new_path = '{}\{}'.format(base, show_name)

                    elif is_movie(guess):
                        new_path = settings.movies_path

                    new_file_path = '{}\{}'.format(new_path, file_name)

                    if settings.move_files:
                        logger.info('Moving file: FROM {} TO {}'.format(file_path, new_file_path))
                        winshell.move_file(file_path, new_path, allow_undo=True, no_confirm=True, silent=False, hWnd=None)  # noqa
                    else:
                        logger.info('Copying file: FROM {} TO {}'.format(file_path, new_file_path))
                        winshell.copy_file(file_path, new_path, allow_undo=True, no_confirm=True, silent=False, hWnd=None)  # noqa

                else:
                    if is_garbage_file(file_path):
                        logger.info('Removing file: {}'.format(file_path))
                        winshell.delete_file(file_path, allow_undo=True, no_confirm=True, silent=False, hWnd=None)

            except AttributeError:
                logger.error(traceback.print_exc())

        # Update XBMC
        logger.info('Update XBMC')
        url = 'http://192.168.1.31:12345/jsonrpc'
        data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
        requests.post(url, json=data)

        delete_dummy_file(dummy_file_path)
    else:
        logger.info('Proses already running')


if __name__ == "__main__":
    # add filemode="w" to overwrite
    main()
