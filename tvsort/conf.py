# coding=utf-8
from __future__ import unicode_literals
import os


class SortSettings(object):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

    tv_path         = 'G:\\TVShows'
    movies_path     = 'G:\\Movies'
    unsorted_path   = 'G:\\Unsortted'
    move_files      = False
    dummy_file_path = '{}\{}'.format(unsorted_path, 'dummy.txt')
    test_file_path  = '{}\{}'.format(unsorted_path, 'test.txt')
    test_file_path_in_tv = '{}\{}'.format(tv_path, 'test.txt')
    log_path        = '{}\\log\\tvsort.log'.format(BASE_DIR)

    # extensions
    compress_exts = ['.r00', 'rar', 'zip']
    media_exts    = ['.mkv', '.avi', '.mp4', '.wemb', '.ogg', '.mov', '.wmv', '.m4v', '.m4p', '.mpg', '.mpeg', '.ogm']

settings = SortSettings()
