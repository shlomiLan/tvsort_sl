import logging
import os
import traceback
from collections import Counter

import daiquiri
import patoolib
import yaml
from guessit import guessit

from tvsort_sl import utils


class TvSort(object):
    project_name = 'tvsort_sl'
    settings = dict(PROJECT_NAME=project_name)
    logger = None

    report = dict(counters=Counter(), errors=[])

    def __init__(self, is_test=False, **kwargs):
        self.base_dir, self.settings_folder = self.get_settings_folders()
        self.load_base_setting()

        if all(message[0] == 'info' for message in self.check_project_setup(is_test)):
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

                # Scan and move/copy videos
                self.scan_videos()

                # UPDATE XBMC
                response = utils.update_xbmc(self.settings.get('KODI_IP'))
                self.process_response(response)

                # CLEAN UP
                for folder_path in utils.get_folders(self.unsorted_path):
                    response = utils.delete_folder_if_empty(folder_path)
                    self.process_response(response)

            except Exception as e:
                self.process_response([('error', traceback.print_exc())])
                self.process_response([('error', str(e))])

            finally:
                response = utils.delete_file(self.settings.get('DUMMY_FILE_PATH'))
                self.process_response(response)

        else:
            self.process_response([('error', 'Proses already running')])

        return self.report

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
        conf_files = self.get_settings_file(is_base=True)
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
        self.settings['TEST_TV_PATH'] = os.path.join(self.settings['TEST_FILES'],
                                                     'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv')  # noqa
        self.settings['TEST_TV_2_PATH'] = os.path.join(self.settings['TEST_FILES'],
                                                       'shameless.us.s08e01.web.h264-convoy.mkv')  # noqa
        self.settings['TEST_TV_3_PATH'] = os.path.join(self.settings['TEST_FILES'],
                                                       'This.Is.Us.S02E01.REPACK.720p.HDTV.x264-AVS.mkv')  # noqa
        self.settings['TEST_MOVIE'] = os.path.join(self.settings['TEST_FILES'],
                                                   'San Andreas 2015 720p WEB-DL x264 AAC-JYK.mkv')  # noqa
        self.settings['TEST_GARBAGE_PATH'] = os.path.join(self.settings['TEST_FILES'], 'test.nfo')
        self.settings['GARBAGE_FILE_DS'] = os.path.join(self.settings['TEST_FILES'], '.DS_Store')
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
            return [('error', f'Logs folder is missing, should be at: {log_folder_path}')]

        # Configs files exists
        for file_path in conf_files:
            if not utils.is_file_exists(file_path):
                return [('error', 'Missing config file, you must have local.yml and test.yml in settings folder. '
                                  'Use files in settings/templates for reference')]

        return [('info', 'Project setup successfully')]

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
                patoolib.extract_archive(file_path, outdir=self.unsorted_path, verbosity=-1)
                self.process_response(['info', f'Extracting {file_path}'])
                response = utils.delete_file(file_path)
                self.process_response(response)

    def scan_videos(self):
        """
        Scan for videos (Movies and Episodes) in 'unsorted_path'
        :return: List of videos
        """
        for file_path in utils.get_files(self.unsorted_path):
            self.process_response([('info', f'Checking file: {file_path}')])

            # GARBAGE_FILE
            if utils.is_garbage_file(file_path, self.settings):
                response = utils.delete_file(file_path)
                self.process_response(response)
                continue

            video = guessit(file_path, options={'expected_title': ['This Is Us']})
            new_path = None

            # Episode
            if utils.is_tv_show(video):
                show_name = utils.transform_to_path_name(video.get('title'))
                utils.add_missing_country(video, show_name)
                if video.get('country'):
                    show_name += '.{}'.format(video.get('country'))

                new_path = os.path.join(self.settings.get('TV_PATH'), show_name)
                response = utils.create_folder(new_path)
                self.process_response(response)

            # Movie
            elif utils.is_movie(video):
                new_path = self.settings.get('MOVIES_PATH')

            # Copy / Move the video file
            response = utils.copy_file(file_path, new_path, move_file=self.settings.get('MOVE_FILES'))
            self.process_response(response)

    def process_response(self, response):
        if response:
            for messages in response:
                msg_type = messages[0]
                msg_text = messages[1]

                if msg_type == 'info':
                    self.logger.info(msg_text)
                    if 'Removing file' in msg_text:
                        self.report.get('counters')['delete'] += 1
                    elif any(text in msg_text for text in ['Moving file', 'Copying file']):
                        self.report.get('counters')['move_or_copy'] += 1
                elif msg_type == 'error':
                    self.logger.error(msg_text)
                    self.report.get('counters')['error'] += 1
                    self.report.get('errors').append(msg_text)


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
