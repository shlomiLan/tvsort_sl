import os

import yaml

from tvsort_sl import utils

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__))).replace('\\', '/')
SETTINGS_FOLDER = os.path.join(BASE_DIR, 'tvsort_sl', 'settings')


def check_project_setup(settings, conf_files):
    log_folder_path = settings.get('LOG_PATH')

    # Logs folder exists
    if not utils.is_folder_exists(log_folder_path):
        return [('error', f'Logs folder is missing, should be at: {log_folder_path}')]

    # Configs files exists
    for file_path in conf_files:
        if not utils.is_file_exists(file_path):
            return [('error', 'Missing config file, you must have local.yml and test.yml in settings folder. '
                              'Use files in settings/templates for reference')]

    return [('info', 'Project setup successfully')]


def get_conf_file_name(is_test=False):
    conf_files = [os.path.join(SETTINGS_FOLDER, 'conf.yml'), os.path.join(SETTINGS_FOLDER, 'local.yml')]

    if is_test:
        conf_files.append(os.path.join(SETTINGS_FOLDER, 'test.yml'))

    return conf_files


def update_settings_from_file(settings, conf_files):
    for file_path in conf_files:
        settings.update(yaml.load(open(file_path)))


def load_setting(settings, conf_files):
    update_settings_from_file(settings, conf_files)
    build_settings(settings)


def build_settings(settings):
    # This should be overwrite by prod OR test settings
    settings['TV_PATH'] = os.path.join(settings.get('BASE_DRIVE'), 'TVShows')
    settings['MOVIES_PATH'] = os.path.join(settings.get('BASE_DRIVE'), 'Movies')
    settings['UNSORTED_PATH'] = os.path.join(settings.get('BASE_DRIVE'), 'Unsortted')
    settings['DUMMY_PATH'] = os.path.join(settings.get('BASE_DRIVE'), 'Dummy')

    settings['TEST_FILES'] = os.path.join(BASE_DIR, 'tvsort_sl', 'tests', 'test_files')
    # This folder should have any files init
    settings['FAKE_PATH'] = os.path.join(settings.get('BASE_DRIVE'), 'xxx')

    settings['DUMMY_FILE_PATH'] = os.path.join(settings.get('TV_PATH'), settings.get('DUMMY_FILE_NAME'))
    settings['TEST_FILE_PATH'] = os.path.join(settings.get('UNSORTED_PATH'), 'test.txt')
    settings['TEST_FILE_PATH_IN_TV'] = os.path.join(settings.get('TV_PATH'), 'test.txt')

    # test files
    settings['TEST_ZIP_PATH'] = os.path.join(settings['TEST_FILES'], 'zip_test.zip')
    settings['TEST_TV_PATH'] = os.path.join(settings['TEST_FILES'],
                                            'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv')
    settings['TEST_TV_2_PATH'] = os.path.join(settings['TEST_FILES'], 'shameless.us.s08e01.web.h264-convoy.mkv')
    settings['TEST_TV_3_PATH'] = os.path.join(settings['TEST_FILES'], 'This.Is.Us.S02E01.REPACK.720p.HDTV.x264-AVS.mkv')
    settings['TEST_MOVIE'] = os.path.join(settings['TEST_FILES'], 'San Andreas 2015 720p WEB-DL x264 AAC-JYK.mkv')
    settings['TEST_GARBAGE_PATH'] = os.path.join(settings['TEST_FILES'], 'test.nfo')
    settings['GARBAGE_FILE_DS'] = os.path.join(settings['TEST_FILES'], '.DS_Store')
    settings['TEST_FOLDER_NAME'] = 'test.nfo'
    settings['TEST_FOLDER_IN_UNSORTED'] = os.path.join(settings.get('UNSORTED_PATH'), 'empty_folder')
