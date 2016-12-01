# coding=utf-8
from __future__ import unicode_literals
import os


class SortSettings(object):
    # Build paths inside the project like this: os.path.join(BASE_DIR, ...)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    PROJECT_ROOT = os.path.abspath(os.path.join(BASE_DIR, os.pardir))

    tv_path              = '\\\movies-pc\\TVShows'
    movies_path          = '\\\movies-pc\\Movies'
    unsorted_path        = '\\\movies-pc\\Unsortted'
    move_files           = True
    dummy_file_name      = 'dummy.txt'
    dummy_file_path      = '{}\{}'.format(tv_path, dummy_file_name)
    test_file_path       = '{}\{}'.format(unsorted_path, 'test.txt')
    test_file_path_in_tv = '{}\{}'.format(tv_path, 'test.txt')
    log_path             = '{}\\log\\tvsort.log'.format(BASE_DIR)

    # extensions
    compress_exts = ['r00', 'rar', 'zip']
    media_exts    = ['mkv', 'avi', 'mp4', 'wemb', 'ogg', 'mov', 'wmv', 'm4v', 'm4p', 'mpg', 'mpeg', 'ogm']
    garbage_exts  = ['nfo', 'txt', 'db', 'pdf', 'jpg', 'png', 'str']

settings = SortSettings()
