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


class TvSort(object):
    def __init__(self, base_drive):
        self.settings = SortSettings(base_drive)
        self.is_any_error = False
        self.path = self.settings.UNSORTED_PATH
        self.dummy_file_path = self.settings.DUMMY_FILE_PATH
        self.logger = self.create_logger()

        print(self.settings.TV_PATH)

    def run(self):
        if not self.is_process_already_running(self.dummy_file_path):
            try:
                self.create_file(self.dummy_file_path)

                print(self.path)
                print(self.get_files(self.path))
                for file_path in self.get_files(self.path):
                    if self.is_compressed(file_path):
                        self.logger.info("Extracting {}".format(file_path))
                        patoolib.extract_archive(file_path, outdir=self.path)
                        self.delete_file(file_path)

                for file_path in self.get_files(self.path):
                    self.logger.info('Checking file: {}'.format(file_path))

                    if self.is_garbage_file(file_path):
                        self.logger.info('Removing file: {}'.format(file_path))
                        self.delete_file(file_path)
                    elif self.is_media(file_path):
                        guess = guessit(file_path)
                        new_path = None
                        if self.is_tv_show(guess):
                            base = self.settings.TV_PATH
                            self.remove_wrong_country_data(guess)
                            show_name = self.transform_to_path_name(self.get_show_name(guess))
                            self.add_missing_country(guess, show_name)
                            if guess.get('country'):
                                show_name += '.{}'.format(guess.get('country'))
                                self.create_folder(show_name)
                            new_path = '{}\{}'.format(base, show_name)

                        elif self.is_movie(guess):
                            new_path = self.settings.MOVIES_PATH

                        new_file_path = '{}\{}'.format(new_path, self.get_file_name(file_path))
                        self.copy_file(file_path, new_path, new_file_path, move_file=self.settings.MOVE_FILES)

                    folder_path = self.get_folder_path_from_file_path(file_path)
                    if self.folder_empty(folder_path):
                        os.rmdir(folder_path)

                # Update XBMC
                self.logger.info('Update XBMC')

                url = '{}/jsonrpc'.format(self.settings.KODI_IP)
                data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
                requests.post(url, json=data)

            except Exception as e:
                self.is_any_error = True
                self.logger.error(e)
                self.logger.error(traceback.print_exc())

            finally:
                self.delete_file(self.dummy_file_path)
                return not self.is_any_error
        else:
            self.logger.info('Proses already running')
            return False

    def create_logger(self):
        logger = logging.getLogger('tvshow')
        logger.level = logging.DEBUG
        logger.addHandler(logging.StreamHandler())
        logger.addHandler(logging.FileHandler(filename=self.settings.LOG_FILE_PATH))

        return logger

    def is_compressed(self, file_name):
        return self.is_file_ext_in_list(self.get_file_ext(file_name), self.settings.COMPRESS_EXTS)

    def is_media(self, file_name):
        return self.is_file_ext_in_list(self.get_file_ext(file_name), self.settings.MEDIA_EXTS)

    def is_garbage_file(self, file_name):
        return self.is_file_ext_in_list(self.get_file_ext(file_name), self.settings.GARBAGE_EXTS) or 'sample' in file_name.lower()

    def is_file_ext_in_list(self, file_ext, ext_list):
        return bool(file_ext in ext_list)

    def get_file_ext(self, file_name):
        return file_name.split('.')[-1]

    def get_file_name(self, file_path):
        return file_path.split('\\')[-1]

    def get_folder_path_from_file_path(self, file_path):
        return '\\'.join(file_path.split('\\')[:-1])

    def get_files(self, path):
        files = []

        for root, dirs, walk_files in os.walk(path):
            for f in walk_files:
                files.append(os.path.join(root, f))

        return sorted(files)

    def is_tv_show(self, guess):
        return bool(guess.get('episode'))

    def is_movie(self, guess):
        return guess.get('type') == 'movie'

    def is_file_exists(self, file_path):
        return os.path.isfile(file_path)

    def is_folder_exists(self, file_path):
        return os.path.isdir(file_path)

    def create_folder(self, folder_path):
        if not os.path.exists(folder_path):
            # retry to delete folder 10 times
            for retry in range(10):
                try:
                    os.makedirs(folder_path)
                    return True
                except:
                    print('Folder deletion failed, retrying...')
            else:
                logging.error("Can't remove folder: {}".format(folder_path))
                return False

        return True

    def delete_folder(self, folder_path):
        try:
            if self.folder_empty(folder_path):
                os.rmdir(folder_path)
                return True
            else:
                self.logger.error("Folder is not empty")
                return False
        except Exception as e:
            self.logger.error("Folder can't be deleted, Unexpected error: {}".format(e))
            return False

    def is_process_already_running(self, file_path):
        return self.is_file_exists(file_path)

    def transform_to_path_name(self, string):
        if isinstance(string, int):
            string = str(string)
        string = re.sub(' ', '.', string)
        return '.'.join([str(x).capitalize() for x in string.split('.')])

    def get_show_name(self, guess):
        return guess.get('title')

    def remove_wrong_country_data(self, guess):
        if guess.get('title') == 'This is':
            guess['title'] += '.Us'
            if guess.get('country'):
                del guess['country']

    def add_missing_country(self, guess, show_name):
        if show_name.lower() == 'house of cards':
            if not guess.get('country'):
                guess['country'] = 'US'

    def create_file(self, file_path):
        dummy_file = open(file_path, str('w'))
        dummy_file.close()

    def delete_file(self, file_path, no_confirm=True):
        try:
            winshell.delete_file(file_path, no_confirm=no_confirm)
            return True
        except Exception as e:
            self.logger.error("Unexpected error: {}".format(e))
            return False

    def copy_file(self, old_path, new_path, new_file_path, move_file=True, no_confirm=True):
        # TODO: remove the 'new_file_path' parameter
        action = 'Moving' if move_file else 'Copying'
        self.logger.info('{} file: FROM {} TO {}'.format(action, old_path, new_file_path))

        print(old_path)
        print(new_path)
        print(new_file_path)
        try:
            if move_file:
                winshell.move_file(old_path, new_path, no_confirm=no_confirm)
            else:
                winshell.copy_file(old_path, new_path, no_confirm=no_confirm)
            return True
        except Exception as e:
            self.logger.error("Unexpected error: {}".format(e))
            return False

    def folder_empty(self, folder_path):
        return not bool(self.get_files(folder_path))

if __name__ == "__main__":
    tv_sort = TvSort(base_drive='\\\movies-pc')
    tv_sort.run()
