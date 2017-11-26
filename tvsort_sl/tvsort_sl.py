# coding=utf-8
from __future__ import unicode_literals

import logging

import daiquiri
import os
import traceback

import yaml
from guessit import guessit
import patoolib
from subliminal import scan_videos, region, Episode, Movie

import utils as utils


class TvSort(object):
    # configure the cache
    region.configure('dogpile.cache.dbm', arguments={'filename': 'cachefile.dbm'})

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

    def run(self):
        if not utils.is_process_already_running(self.settings.get('DUMMY_FILE_PATH')):
            try:
                utils.create_file(self.settings.get('DUMMY_FILE_PATH'))
                unsorted_path = self.settings.get('UNSORTED_PATH')

                # scan for videos in the unsorted foolder
                # TODO: is the str() necessary???
                videos = scan_videos(str(unsorted_path))

                for video in videos:
                    if isinstance(video, (Episode, Movie)):
                        new_path = None
                        file_path = video.name
                        file_name = utils.get_file_name(file_path)
                        print('file name is: {}'.format(file_name))
                        print(video.__dict__)
                        self.logger.info('Checking file: {}'.format(file_path))

                        # Episode
                        if isinstance(video, Episode):
                            video_name = utils.transform_to_path_name(video.series)
                            if video.country:
                                video_name += '.{}'.format(video.country)

                            new_path = os.path.join(self.settings.get('TV_PATH'), video_name)
                            utils.create_folder(new_path, self.logger)

                        # Movie
                        elif isinstance(video, Movie):
                            new_path = self.settings.get('MOVIES_PATH')

                        # Copy / Move the video file
                        # utils.copy_file(file_path, new_path, self.logger, move_file=self.settings.get('MOVE_FILES'))

                        # Change the video name (path)
                        print('path is: {}'.format(new_path))
                        video.name = os.path.join(new_path, file_name)

                    # GARBAGE_FILE
                    # if utils.is_garbage_file(video.name, self.settings):
                    #     self.logger.info('Removing file: {}'.format(file_path))
                    #     utils.delete_file(file_path, self.logger)
                    #     continue

                    # ARCHIVES
                        # for file_path in utils.get_files(self.settings.get('UNSORTED_PATH')):
                #     if utils.is_compressed(file_path, self.settings):
                #         self.logger.info("Extracting {}".format(file_path))
                #         patoolib.extract_archive(file_path, outdir=self.settings.get('UNSORTED_PATH'), verbosity=-1)
                #         utils.delete_file(file_path, self.logger)
                #
                # CLEAN UP
                #     folder_path = utils.get_folder_path_from_file_path(file_path)
                #     utils.delete_folder_if_empty(folder_path, self.logger)
                #
                #
                # for folder_path in utils.get_folders(self.settings.get('UNSORTED_PATH')):
                #     utils.delete_folder_if_empty(folder_path, self.logger)
                #
                # DOWNLOAD SUBTITLES
                utils.download_subtitles(videos)

                # UPDATE XBMC
                # utils.update_xbmc(self.settings.get('KODI_IP'), self.logger)

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

            return conf_files

    def update_settings_from_file(self, conf_files):
        for file_path in conf_files:
            self.settings.update(yaml.load(open(file_path)))

    def build_base_settings(self):
        self.settings['LOG_PATH'] = os.path.join(self.base_dir, 'logs')

    def load_additional_settings(self, is_test=False):
        conf_files = self.get_settings_file(is_base=False, is_test=is_test)
        self.update_settings_from_file(conf_files)

        self.build_settings()

    def build_settings(self):
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
        self.settings['TEST_ZIP_NAME'] = 'zip_test.zip'
        self.settings['TEST_TV_NAME'] = 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'
        self.settings['TEST_MOVIE'] = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK.mkv'
        self.settings['TEST_GARBAGE_NAME'] = 'test.nfo'
        self.settings['TEST_FOLDER_NAME'] = 'test.nfo'
        self.settings['TEST_FOLDER_IN_UNSORTED'] = os.path.join(self.settings.get('UNSORTED_PATH'), 'empty_folder')

    def check_project_setup(self, is_test):
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
        daiquiri.setup(outputs=(
            daiquiri.output.File(directory=self.settings.get('LOG_PATH'),
                                 program_name=self.project_name), daiquiri.output.STDOUT,))

        daiquiri.getLogger(program_name=self.project_name).logger.level = log_level
        self.logger = daiquiri.getLogger(program_name=self.project_name, log_level=log_level)


if __name__ == "__main__":
    tv_sort = TvSort()
    tv_sort.run()
