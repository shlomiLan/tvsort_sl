# coding=utf-8
from __future__ import unicode_literals

import logging

import daiquiri
import os
import traceback

import yaml
import patoolib
from guessit import guessit

import tvsort_sl.utils as utils


class TvSort(object):
    is_any_error = False
    project_name = 'tvsort_sl'
    settings = dict(PROJECT_NAME=project_name)
    logger = None

    def __init__(self, is_test=False, **kwargs):
        self.base_dir, self.settings_folder = self.get_settings_folders()
        self.load_base_setting()

        if self.check_project_setup(is_test):
            self.load_additional_settings(is_test=is_test)

            self.create_logger(**kwargs)

        self.unsorted_path = self.settings.get('UNSORTED_PATH')

    def run(self):
        """
        Run the tvsort process
        :return:
        """
        if not utils.is_process_already_running(self.settings.get('DUMMY_FILE_PATH')):
            try:
                utils.create_file(self.settings.get('DUMMY_FILE_PATH'))

                # Scan and Extract all compressed files
                self.scan_archives()

                # UPDATE XBMC
                utils.update_xbmc(self.settings.get('KODI_IP'), self.logger)

                # CLEAN UP
                for folder_path in utils.get_folders(self.unsorted_path):
                    utils.delete_folder_if_empty(folder_path, self.logger)

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
        """
        Paths for base folder and the settings folder
        :return: Base die path and setting folder path
        """
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        settings_folder = os.path.join(base_dir, self.project_name, 'settings')

        return base_dir, settings_folder

    def load_base_setting(self):
        """
        Load the basic settings
        """
        conf_files = self.get_settings_file(self.settings_folder)
        self.update_settings_from_file(conf_files)

        self.build_base_settings()

    def get_settings_file(self, is_base=True, is_test=False):
        """
        Get a list of all setting file paths
        :param is_base: load base settings
        :type is_base: bool
        :param is_test: is test run
        :type is_test: bool
        :return: List of all setting file paths
        """
        if is_base:
            return [os.path.join(self.settings_folder, 'conf.yml')]
        else:
            conf_files = [os.path.join(self.settings_folder, 'local.yml')]
            if is_test:
                conf_files.append(os.path.join(self.settings_folder, 'test.yml'))

            return conf_files

    def update_settings_from_file(self, conf_files):
        """
        Add to settings from file
        :param conf_files: List of config files
        :type conf_files: list
        """
        for file_path in conf_files:
            self.settings.update(yaml.load(open(file_path)))

    def build_base_settings(self):
        """
        build the basic settings
        """
        self.settings['LOG_PATH'] = os.path.join(self.base_dir, 'logs')

    def load_additional_settings(self, is_test=False):
        """
        load the additional settings from file
        :param is_test: is test run
        :type is_test: bool
        """
        conf_files = self.get_settings_file(is_base=False, is_test=is_test)
        self.update_settings_from_file(conf_files)

        self.build_settings()

    def build_settings(self):
        """
        Build the settings (all of it)
        """
        # This should be overwrite by prod OR test settings
        self.settings['TV_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'TVShows')
        self.settings['MOVIES_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Movies')
        self.settings['UNSORTED_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Unsortted')
        self.settings['DUMMY_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'Dummy')

        self.settings['TEST_FILES'] = os.path.join(self.base_dir, 'tvsort_sl', 'tests', 'test_files')
        # This folder should have any files init
        self.settings['FAKE_PATH'] = os.path.join(self.settings.get('BASE_DRIVE'), 'xxx')

        self.settings['DUMMY_FILE_PATH'] = os.path.join(self.settings.get('TV_PATH'),
                                                        self.settings.get('DUMMY_FILE_NAME'))
        self.settings['TEST_FILE_PATH'] = os.path.join(self.settings.get('UNSORTED_PATH'), 'test.txt')
        self.settings['TEST_FILE_PATH_IN_TV'] = os.path.join(self.settings.get('TV_PATH'), 'test.txt')

        # test files
        self.settings['TEST_ZIP_PATH'] = os.path.join(self.settings['TEST_FILES'], 'zip_test.zip')
        self.settings['TEST_TV_PATH'] = os.path.join(self.settings['TEST_FILES'], 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv')   # noqa
        self.settings['TEST_TV_2_PATH'] = os.path.join(self.settings['TEST_FILES'], 'shameless.us.s08e01.web.h264-convoy.mkv')  # noqa
        self.settings['TEST_TV_3_PATH'] = os.path.join(self.settings['TEST_FILES'], 'This.Is.Us.S02E01.REPACK.720p.HDTV.x264-AVS.mkv')  # noqa
        self.settings['TEST_MOVIE'] = os.path.join(self.settings['TEST_FILES'], 'San Andreas 2015 720p WEB-DL x264 AAC-JYK.mkv')  # noqa
        self.settings['TEST_GARBAGE_PATH'] = os.path.join(self.settings['TEST_FILES'], 'test.nfo')
        self.settings['TEST_FOLDER_NAME'] = 'test.nfo'
        self.settings['TEST_FOLDER_IN_UNSORTED'] = os.path.join(self.settings.get('UNSORTED_PATH'), 'empty_folder')

    def check_project_setup(self, is_test):
        """
        Test that all the project setup is set, if not raise an exception
        :param is_test: is test run
        :type is_test: bool
        :return: Flag to indicate if the project setup correctly
        """
        log_folder_path = self.settings.get('LOG_PATH')
        conf_files = self.get_settings_file(is_base=False, is_test=is_test)
        # Logs folder exists
        if not utils.is_folder_exists(log_folder_path):
            raise Exception('Logs folder is missing, should be at: {}'.format(log_folder_path))

        # Configs files exists
        for file_path in conf_files:
            if not utils.is_file_exists(file_path):
                raise Exception('Missing config file, you must have local.yml and test.yml in settings folder.'
                                'Use files in settings/templates for reference')

        return True

    def create_logger(self, log_level=logging.INFO):
        """
        Create the logger that all functions will use
        :param log_level: log level to use when creating the logger
        :type log_level: basestring
        """
        daiquiri.setup(outputs=(
            daiquiri.output.File(directory=self.settings.get('LOG_PATH'),
                                 program_name=self.project_name), daiquiri.output.STDOUT,))

        daiquiri.getLogger(program_name=self.project_name).logger.level = log_level
        self.logger = daiquiri.getLogger(program_name=self.project_name, log_level=log_level)

    def scan_archives(self):
        """
        Scan the 'unsorted_path' for archives file and extract them
        """
        for file_path in utils.get_files(self.unsorted_path):
            if utils.is_compressed(file_path, self.settings):
                self.logger.info("Extracting {}".format(file_path))
                patoolib.extract_archive(file_path, outdir=self.unsorted_path, verbosity=-1)
                utils.delete_file(file_path, self.logger)

    def scan_videos(self):
        """
        Scan for videos (Movies and Episodes) in 'unsorted_path'
        :return: List of videos
        """
        for file_path in utils.get_files(self.unsorted_path):
            self.logger.info('Checking file: {}'.format(file_path))

            # GARBAGE_FILE
            if utils.is_garbage_file(file_path, self.settings):
                self.logger.info('Removing file: {}'.format(file_path))
                utils.delete_file(file_path, self.logger)
                continue

            video = guessit(file_path, options={"expected_title": ["This Is Us"]})
            new_path = None
            file_path = video.name
            self.logger.info('Checking file: {}'.format(file_path))

            # Episode
            if utils.is_tv_show(video):
                video_name = utils.transform_to_path_name(video.series)
                utils.add_missing_country(video, video_name)
                if video.country:
                    video_name += '.{}'.format(video.country)

                new_path = os.path.join(self.settings.get('TV_PATH'), video_name)
                utils.create_folder(new_path, self.logger)

            # Movie
            elif utils.is_movie(video):
                new_path = self.settings.get('MOVIES_PATH')
            else:
                self.logger('Unsupported file type in: {}'.format(file_path))

            # Copy / Move the video file
            utils.copy_file(file_path, new_path, self.logger, move_file=self.settings.get('MOVE_FILES'))


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
