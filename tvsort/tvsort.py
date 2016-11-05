import traceback

import winshell
from guessit import guessit
from opster import command
import os
import shutil
import patoolib
import logging

from conf import settings


def is_compressed(path):
    return any(path.lower().endswith(ext) for ext in settings.compress_exts)


def is_media(path):
    return any(path.lower().endswith(ext) for ext in settings.media_exts)


def get_files(path):
    files = []
    if os.path.isfile(path):
        files.append(path)

    for root, dirs, walk_files in os.walk(path):
        for f in walk_files:
            f_path = os.path.join(root, f)
            if "sample" in f_path.lower():
                continue
            else:
                files.append(f_path)
    
    return sorted(files)


def is_tv_show(guess):
    return guess.get('type') == 'episode'


def is_movie(guess):
    return guess.get('type') == 'movie'


def is_file_exists(file_path):
    try:
        os.remove(file_path)
        old_file = open(file_path, 'w')
        old_file.close()
        return True
    except:
        return False


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


def remove_file(file_path):
    try:
        os.remove(file_path)
    except:
        return False

    return True


def is_process_already_run(file_path):
    if is_file_exists(file_path):
        return True
    else:
        return False


def transform_to_path_name(string):
    if isinstance(string, int):
        string = str(string)
    string_as_list = [x.capitalize() for x in string.split(' ')]
    return '.'.join(string_as_list)


@command()
def main():
    logger = create_logger()
    path = settings.unsorted_path
    dummy_file_path = settings.dummy_file_path

    if not is_process_already_run(dummy_file_path):
        dummy_file = open(dummy_file_path, 'w')
        dummy_file.close()

        for file_path in get_files(path):
            if is_compressed(file_path):
                logger.info("Extracting {}".format(file_path))
                patoolib.extract_archive(file_path, outdir=path)
                remove_file(file_path)

        for file_path in get_files(path):
            try:
                if is_media(file_path):
                    guess = guessit(file_path)
                    new_path = None
                    if is_tv_show(guess):
                        base = settings.tv_path
                        show_name = guess.get('title')
                        show_name = transform_to_path_name(show_name)
                        create_folder(show_name, base)
                        new_path = '{}\{}'.format(base, show_name)

                    elif is_movie(guess):
                        new_path = settings.movies_path

                    if is_file_exists(new_path):
                        logger.info('Removing file: FROM {}'.format(file_path, new_path))
                        os.remove(new_path)

                    if settings.move_files:
                        logger.info('Moving file: FROM {} TO {}'.format(file_path, new_path))
                        winshell.move_file(file_path, new_path, allow_undo=True, no_confirm=False, silent=False, hWnd=None)  # noqa
                    else:
                        logger.info('Copying file: FROM {} TO {}'.format(file_path, new_path))
                        winshell.copy_file(file_path, new_path, allow_undo=True, no_confirm=False, silent=False, hWnd=None)  # noqa

            except AttributeError:
                logger.error(traceback.print_exc())
            except:
                logger.error('Unexpected error: {}'.format(traceback.print_exc()))

        remove_file(dummy_file_path)

    else:
        logger.info('Proses already running')


if __name__ == "__main__":
    # add filemode="w" to overwrite
    main()
