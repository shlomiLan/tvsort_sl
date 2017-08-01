# coding=utf-8
from __future__ import unicode_literals

import traceback

from guessit import guessit
import os
import patoolib

import utils


class TvSort(object):
    is_any_error = False

    def __init__(self, is_test=False, **kwargs):
        self.settings = utils.load_settings(is_test=is_test)

        if self.check_project_setup():
            self.logger = utils.create_logger(self.settings['LOG_PATH'], self.settings.get('PROJECT_NAME'), **kwargs)

    def check_project_setup(self):
        log_folder_path = self.settings.get('LOG_PATH')
        if not utils.is_folder_exists(log_folder_path):
            raise Exception('{} folder in missing'.format(log_folder_path))

        return True

    def run(self):
        if not utils.is_process_already_running(self.settings.get('DUMMY_FILE_PATH')):
            try:
                utils.create_file(self.settings.get('DUMMY_FILE_PATH'))

                for file_path in utils.get_files(self.settings.get('UNSORTED_PATH')):
                    if utils.is_compressed(file_path, self.settings):
                        self.logger.info("Extracting {}".format(file_path))
                        patoolib.extract_archive(file_path, outdir=self.settings.get('UNSORTED_PATH'), verbosity=-1)
                        utils.delete_file(file_path, self.logger)

                for file_path in utils.get_files(self.settings.get('UNSORTED_PATH')):
                    self.logger.info('Checking file: {}'.format(file_path))

                    if utils.is_garbage_file(file_path, self.settings):
                        self.logger.info('Removing file: {}'.format(file_path))
                        utils.delete_file(file_path, self.logger)
                    elif utils.is_media(file_path, self.settings):
                        guess = guessit(file_path)
                        new_path = None
                        if utils.is_tv_show(guess):
                            base = self.settings.get('TV_PATH')
                            utils.remove_wrong_country_data(guess)
                            show_name = utils.transform_to_path_name(utils.get_show_name(guess))
                            utils.add_missing_country(guess, show_name)
                            if guess.get('country'):
                                show_name += '.{}'.format(guess.get('country'))

                            new_path = '{}\{}'.format(base, show_name)
                            utils.create_folder(new_path, self.logger)

                        elif utils.is_movie(guess):
                            new_path = self.settings.get('MOVIES_PATH')

                        utils.copy_file(file_path, new_path, self.logger, move_file=self.settings.get('MOVE_FILES'))

                    folder_path = utils.get_folder_path_from_file_path(file_path)
                    if utils.folder_empty(folder_path):
                        if not self.settings.get('UNSORTED_PATH'):
                            os.rmdir(folder_path)

                # Update XBMC
                utils.update_xbmc(self.settings.get('KODI_IP'), self.logger)

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
