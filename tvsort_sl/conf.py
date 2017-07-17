# coding=utf-8
from __future__ import unicode_literals
import os


class SortSettings(object):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

    TV_PATH              = '\\\movies-pc\\TVShows'
    MOVIES_PATH          = '\\\movies-pc\\Movies'
    UNSORTED_PATH        = '\\\movies-pc\\Unsortted'
    DUMMY_PATH           = '\\\movies-pc\\Unsortted'

    KODI_IP = 'http://192.168.1.31:12345'

    # move OR copy files
    MOVE_FILES           = True

    DUMMY_FILE_NAME      = 'dummy.txt'
    DUMMY_FILE_PATH      = '{}\{}'.format(TV_PATH, DUMMY_FILE_NAME)
    TEST_FILE_PATH       = '{}\{}'.format(UNSORTED_PATH, 'test.txt')
    TEST_FILE_PATH_IN_TV = '{}\{}'.format(TV_PATH, 'test.txt')
    LOG_PATH             = '{}\\log\\tvsort.log'.format(BASE_DIR)

    # extensions
    COMPRESS_EXTS = ['r00', 'rar', 'zip']
    MEDIA_EXTS    = ['mkv', 'avi', 'mp4', 'wemb', 'ogg', 'mov', 'wmv', 'm4v', 'm4p', 'mpg', 'mpeg', 'ogm']
    GARBAGE_EXTS  = ['nfo', 'txt', 'db', 'pdf', 'jpg', 'png', 'srt']

settings = SortSettings()
