# coding=utf-8
from __future__ import unicode_literals

import logging

import daiquiri
import os
import traceback

import yaml
from guessit import guessit
import patoolib

import utils


class TvSort(object):
    is_any_error = False
    project_name = 'tvsort_sl'
    settings = dict(PROJECT_NAME=project_name)
    logger = None

    def __init__(self, is_test=False, **kwargs):
        self.base_dir, self.settings_folder = self.get_settings_folders()
        self.load_base_setting()

        if self.check_project_setup():
            self.load_additional_settings(is_test=is_test)

            self.create_logger(**kwargs)

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

                            new_path = os.path.join(base, show_name)
                            utils.create_folder(new_path, self.logger)

                        elif utils.is_movie(guess):
                            new_path = self.settings.get('MOVIES_PATH')

                        utils.copy_file(file_path, new_path, self.logger, move_file=self.settings.get('MOVE_FILES'))

                    folder_path = utils.get_folder_path_from_file_path(file_path)
                    utils.delete_folder_if_empty(folder_path, self.logger)

                # clean up
                for folder_path in utils.get_folders(self.settings.get('UNSORTED_PATH')):
                    utils.delete_folder_if_empty(folder_path, self.logger)

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

    def get_settings_folders(self):
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_folder = os.path.join(base_dir, self.project_name, 'settings')

        return base_dir, settings_folder

    def load_base_setting(self):
        conf_files = self.get_settings_file(self.settings_folder)
        self.update_settings_from_file(conf_files)

        self.build_base_settings()

    def get_settings_file(self, is_base=True, is_test=False):
        if is_base:
            return [os.path.join(self.settings_folder, 'conf.yml')]
        else:
            conf_files = [os.path.join(self.settings_folder, 'local.yml')]
            if is_test:
                conf_files.append(os.path.join(self.settings_folder, 'test.yml'))

    def update_settings_from_file(self, conf_files):
        for file_path in conf_files:
            self.settings.update(yaml.load(open(file_path)))

    def build_base_settings(self):
        self.settings['LOG_PATH'] = os.path.join(self.base_dir, 'logs')

    def load_additional_settings(self, is_test=False):
        conf_files = self.get_settings_file(is_base=False, is_test=is_test)
        self.update_settings_from_file(conf_files)

    def build_settings(self):
        # This should be overwrite by prod OR test settings
        self.settings['TV_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'TVShows')
        self.settings['MOVIES_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Movies')
        self.settings['UNSORTED_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Unsortted')
        self.settings['DUMMY_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Dummy')

        self.settings['TEST_FILES'] = os.path.join('base_dir', 'tvsort_sl', 'test_files')
        # This folder should have any files init
        self.settings['FAKE_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'xxx')

        self.settings['DUMMY_FILE_PATH'] = os.path.join(self.settings.get('TV_PATH'),
                                                        self.settings.get('DUMMY_FILE_NAME'))
        self.settings['TEST_FILE_PATH'] = os.path.join(self.settings.get('UNSORTED_PATH'), 'test.txt')
        self.settings['TEST_FILE_PATH_IN_TV'] = os.path.join(self.settings.get('TV_PATH'), 'test.txt')

        # test files
        self.settings['TEST_ZIP_NAME'] = 'zip_test.zip'
        self.settings['TEST_TV_NAME'] = 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'
        self.settings['TEST_MOVIE'] = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK.mkv'
        self.settings['TEST_GARBAGE_NAME'] = 'test.nfo'
        self.settings['TEST_FOLDER_NAME'] = 'test.nfo'
        self.settings['TEST_FOLDER_IN_UNSORTED'] = os.path.join(self.settings.get('UNSORTED_PATH'), 'empty_folder')

    def check_project_setup(self):
        log_folder_path = self.settings.get('LOG_PATH')
        base_config_file = self.get_settings_file()
        # Logs folder exists
        if not utils.is_folder_exists(log_folder_path):
            raise Exception('{} folder in missing'.format(log_folder_path))

        # Configs files exists
        for file_path in base_config_file:
            if not utils.is_file_exists(file_path):
                raise Exception('Missing config file, you must have local.yml and test.yml in settings folder.'
                                'Use files in settings/templates for reference')

        return True

    def create_logger(self, log_level=logging.INFO):
        daiquiri.setup(outputs=(
            daiquiri.output.File(directory=self.settings.get('LOG_PATH'),
                                 program_name=self.project_name), daiquiri.output.STDOUT,))

        daiquiri.getLogger(program_name=self.project_name).logger.level = log_level
        self.logger = daiquiri.getLogger(program_name=self.project_name, log_level=log_level)


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
