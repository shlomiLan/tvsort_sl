# coding=utf-8
from __future__ import unicode_literals
import os


class SortSettings(object):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    KODI_IP = 'http://192.168.1.31:12345'

    # move OR copy files
    MOVE_FILES = True

    DUMMY_FILE_NAME = 'dummy.txt'

    # extensions
    COMPRESS_EXTS = ['r00', 'rar', 'zip']
    MEDIA_EXTS    = ['mkv', 'avi', 'mp4', 'wemb', 'ogg', 'mov', 'wmv', 'm4v', 'm4p', 'mpg', 'mpeg', 'ogm']
    GARBAGE_EXTS  = ['nfo', 'txt', 'db', 'pdf', 'jpg', 'png', 'srt']

    def __init__(self, base_drive):
        # This should be overwrite by prod OR test settings
        self.base_drive    = base_drive
        self.TV_PATH       = '{}\\TVShows'.format(self.base_drive)
        self.MOVIES_PATH   = '{}\\Movies'.format(self.base_drive)
        self.UNSORTED_PATH = '{}\\Unsortted'.format(self.base_drive)
        self.DUMMY_PATH    = '{}\\Dummy'.format(self.base_drive)
        self.LOG_PATH      = '{}\\log'.format(self.BASE_DIR)
        self.TEST_FILES    = '{}\\tvsort_sl\\test_files'.format(self.BASE_DIR)
        # This folder should have any files init
        self.FAKE_PATH     = '{}\\xxx'.format(self.base_drive)

        self.DUMMY_FILE_PATH      = '{}\{}'.format(self.TV_PATH, self.DUMMY_FILE_NAME)
        self.TEST_FILE_PATH       = '{}\{}'.format(self.UNSORTED_PATH, 'test.txt')
        self.TEST_FILE_PATH_IN_TV = '{}\{}'.format(self.TV_PATH, 'test.txt')
        self.LOG_FILE_PATH        = '{}\{}'.format(self.BASE_DIR, 'tvsort.log')
        self.TEST_ZIP_name        = 'zip_test.zip'
