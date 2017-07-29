# coding=utf-8
from __future__ import unicode_literals

import traceback

import requests

from guessit import guessit
import os
import patoolib

import utils


class TvSort(object):
    settings = utils.load_settings()
    is_any_error = False
    path = settings.get('UNSORTED_PATH')
    dummy_file_path = settings.get('DUMMY_FILE_PATH')
    logger = utils.create_logger(settings['LOG_PATH'], settings.get('PROJECT_NAME'))

    def run(self):
        if not utils.is_process_already_running(self.settings.get('DUMMY_FILE_PATH')):
            try:
                utils.create_file(self.settings.get('DUMMY_FILE_PATH'))

                for file_path in utils.get_files(self.settings.get('PATH')):
                    if utils.is_compressed(file_path, self.logger):
                        self.logger.info("Extracting {}".format(file_path))
                        patoolib.extract_archive(file_path, outdir=self.settings.get('UNSORTED_PATH'))
                        utils.delete_file(file_path, self.logger)

                for file_path in utils.get_files(self.settings.get('UNSORTED_PATH')):
                    self.logger.info('Checking file: {}'.format(file_path))

                    if utils.is_garbage_file(file_path, self.logger):
                        self.logger.info('Removing file: {}'.format(file_path))
                        utils.delete_file(file_path, self.logger)
                    elif utils.is_media(file_path, self.logger):
                        guess = guessit(file_path)
                        new_path = None
                        if utils.is_tv_show(guess):
                            base = self.settings.get('TV_PATH')
                            utils.remove_wrong_country_data(guess)
                            show_name = utils.transform_to_path_name(utils.get_show_name(guess))
                            utils.add_missing_country(guess, show_name)
                            if guess.get('country'):
                                show_name += '.{}'.format(guess.get('country'))
                                utils.create_folder(show_name, self.logger)
                            new_path = '{}\{}'.format(base, show_name)

                        elif utils.is_movie(guess):
                            new_path = self.settings.get('MOVIES_PATH')

                        utils.copy_file(file_path, new_path, self.logger, move_file=self.settings.get('MOVE_FILES'))

                    folder_path = utils.get_folder_path_from_file_path(file_path)
                    if utils.folder_empty(folder_path):
                        os.rmdir(folder_path)

                # Update XBMC
                self.logger.info('Update XBMC')

                url = '{}/jsonrpc'.format(self.settings.get('KODI_IP'))
                data = {"jsonrpc": "2.0", "method": "VideoLibrary.Scan", "id": "1"}
                requests.post(url, json=data)

            except Exception as e:
                utils.is_any_error = True
                self.logger.error(e)
                self.logger.error(traceback.print_exc())

            finally:
                utils.delete_file(self.settings.get('DUMMY_FILE_PATH'), self.logger)
                return not self.is_any_error
        else:
            self.logger.info('Proses already running')
            return False


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
