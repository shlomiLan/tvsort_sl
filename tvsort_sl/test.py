# coding=utf-8
from __future__ import unicode_literals

import logging
import unittest

from guessit import guessit
from mock import mock

import utils
from tvsort_sl import TvSort


class TvSortTest(unittest.TestCase):
    tv_sort = TvSort(is_test=True, log_level=logging.FATAL)

    def setUp(self):
        utils.create_folder(self.tv_sort.settings.get('TV_PATH'), self.tv_sort.logger)
        utils.create_folder(self.tv_sort.settings.get('DUMMY_PATH'), self.tv_sort.logger)
        utils.create_folder(self.tv_sort.settings.get('MOVIES_PATH'), self.tv_sort.logger)
        utils.create_folder(self.tv_sort.settings.get('UNSORTED_PATH'), self.tv_sort.logger)

    def tearDown(self):
        utils.delete_folder(self.tv_sort.settings.get('TV_PATH'), self.tv_sort.logger)
        utils.delete_folder(self.tv_sort.settings.get('DUMMY_PATH'), self.tv_sort.logger)
        utils.delete_folder(self.tv_sort.settings.get('MOVIES_PATH'), self.tv_sort.logger)
        utils.delete_folder(self.tv_sort.settings.get('UNSORTED_PATH'), self.tv_sort.logger)

    def test_main(self):
        zip_file_name = self.tv_sort.settings.get('TEST_ZIP_name')
        zip_file_path = '{}\{}'.format(self.tv_sort.settings.get('TEST_FILES'), zip_file_name)
        new_zip_file_folder = self.tv_sort.settings.get('UNSORTED_PATH')
        new_test_file_path = '{}\{}'.format(new_zip_file_folder, zip_file_name)
        utils.copy_file(zip_file_path, new_zip_file_folder, self.tv_sort.logger, move_file=False)
        self.assertTrue(self.tv_sort.run())

    @mock.patch('tvsort_sl.utils.is_folder_exists', return_value=False)
    def test_no_logs_folder(self, is_folder_exists_function):
        self.assertRaises(Exception, self.tv_sort.check_project_setup)

    def test_is_file_exists(self):
        file_path = self.tv_sort.settings.get('TEST_FILE_PATH')
        self.assertFalse(utils.is_file_exists(file_path))
        utils.create_file(file_path)
        self.assertTrue(utils.is_file_exists(file_path))
        utils.delete_file(file_path, self.tv_sort.logger)

    def test_process_not_running(self):
        self.assertFalse(utils.is_process_already_running(self.tv_sort.settings.get('DUMMY_FILE_PATH')))

    def test_process_is_running(self):
        dummy_file_path = self.tv_sort.settings.get('DUMMY_FILE_PATH')
        utils.create_file(dummy_file_path)
        self.assertTrue(utils.is_process_already_running(self.tv_sort.settings.get('DUMMY_FILE_PATH')))
        utils.delete_file(dummy_file_path, self.tv_sort.logger)

    def test_transform_to_path_name(self):
        original_text = 'This is a string with space.s and dots.'
        new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
        self.assertEquals(utils.transform_to_path_name(original_text), new_text)

    def test_replace_space_with_dots_int_input(self):
        string = 1
        self.assertEquals(utils.transform_to_path_name(string), '1')

    def test_not_tv_show(self):
        file_name = str('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
        guess = guessit(file_name)
        self.assertFalse(utils.is_tv_show(guess))

    def test_is_tv_show(self):
        file_name = str('Mr Robot S01E05 HDTV x264-KILLERS[ettv]')
        guess = guessit(file_name)
        self.assertTrue(utils.is_tv_show(guess))

    def test_is_movie(self):
        file_name = str('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
        guess = guessit(file_name)
        self.assertTrue(utils.is_movie(guess))

    def test_compressed_file(self):
        file_name = 'test.zip'
        self.assertTrue(utils.is_compressed(file_name, self.tv_sort.settings))

    def test_not_compressed_file(self):
        file_name = 'test.avi'
        self.assertFalse(utils.is_compressed(file_name, self.tv_sort.settings))

    def test_file_in_ext_list(self):
        self.assertTrue(utils.is_file_ext_in_list('zip', self.tv_sort.settings.get('COMPRESS_EXTS')))

    def test_file_not_in_ext_list(self):
        self.assertFalse(utils.is_file_ext_in_list('avi', self.tv_sort.settings.get('COMPRESS_EXTS')))

    def test_garbage_file(self):
        self.assertFalse(utils.is_garbage_file('test.avi', self.tv_sort.settings))

    def test_media_file(self):
        self.assertTrue(utils.is_media('test.avi', self.tv_sort.settings))

    def test_show_name(self):
        guess = guessit(str('Anger.Management.S01E01.720p.HDTV.x264-IMMERSE.mkv'))
        show_name = utils.get_show_name(guess)
        self.assertEquals(show_name, 'Anger Management')

    def test_folder_exist(self):
        folder_path = self.tv_sort.settings.get('FAKE_PATH')
        self.assertFalse(utils.is_folder_exists(folder_path))
        self.assertFalse(utils.delete_folder(folder_path, self.tv_sort.logger))
        folder_path = self.tv_sort.settings.get('TV_PATH')
        self.assertTrue(utils.is_folder_exists(folder_path))

    def test_delete_folder(self):
        self.assertTrue(utils.delete_folder(self.tv_sort.settings.get('UNSORTED_PATH'), self.tv_sort.logger))
        utils.create_folder(self.tv_sort.settings.get('UNSORTED_PATH'), self.tv_sort.logger)

    def test_empty_folder(self):
        folder_path = self.tv_sort.settings.get('DUMMY_PATH')
        self.assertTrue(utils.folder_empty(folder_path))

    def test_not_empty_folder(self):
        file_name = 'dummy1.txt'
        folder_path = self.tv_sort.settings.get('DUMMY_PATH')
        file_path = '{}\{}'.format(folder_path, file_name)
        utils.create_file(file_path)
        self.assertFalse(utils.folder_empty(folder_path))
        self.assertFalse(utils.delete_folder(folder_path, self.tv_sort.logger))
        utils.delete_file(file_path, self.tv_sort.logger)

    def test_wrong_series_name(self):
        guess = guessit(str('House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'))
        show_name = utils.get_show_name(guess)
        utils.add_missing_country(guess, show_name)
        self.assertEquals(guess.get('country'), 'US')

    def test_wrong_country_data_in_series_name(self):
        guess = guessit(str('This.is.Us.S01E01.HDTV.x264-KILLERS.mkv'))
        utils.remove_wrong_country_data(guess)
        self.assertEquals(guess.get('country'), None)

    def test_get_file_ext(self):
        file_name = 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'
        file_ext = utils.get_file_ext(file_name)
        self.assertEquals('mkv', file_ext)

    def test_delete_file(self):
        dummy_file_path = self.tv_sort.settings.get('DUMMY_FILE_PATH')
        utils.create_file(dummy_file_path)
        self.assertTrue(utils.delete_file(dummy_file_path, self.tv_sort.logger))

    def test_delete_file_fail(self):
        dummy_file_path = self.tv_sort.settings.get('DUMMY_FILE_PATH')
        self.assertFalse(utils.delete_file(dummy_file_path, self.tv_sort.logger))

    def test_move_file(self):
        test_file_path = self.tv_sort.settings.get('TEST_FILE_PATH')
        utils.create_file(test_file_path)
        new_path = self.tv_sort.settings.get('TV_PATH')
        new_test_file_path = '{}\{}'.format(new_path, utils.get_file_name(test_file_path))
        self.assertTrue(utils.copy_file(test_file_path, new_path, self.tv_sort.logger))
        # Clean-up
        utils.delete_file(new_test_file_path, self.tv_sort.logger)

    def test_copy_file(self):
        test_file_path = self.tv_sort.settings.get('TEST_FILE_PATH')
        utils.create_file(test_file_path)
        new_path = self.tv_sort.settings.get('TV_PATH')
        new_test_file_path = '{}\{}'.format(new_path, utils.get_file_name(test_file_path))
        self.assertTrue(utils.copy_file(test_file_path, new_path, self.tv_sort.logger, move_file=False))
        # Delete both files
        utils.delete_file(test_file_path, self.tv_sort.logger)
        utils.delete_file(new_test_file_path, self.tv_sort.logger)

    def test_copy_file_fail(self):
        test_file_path = self.tv_sort.settings.get('TEST_FILE_PATH')
        new_path = self.tv_sort.settings.get('TV_PATH')
        self.assertFalse(utils.copy_file(test_file_path, new_path, self.tv_sort.logger))

    def test_get_folder_name_from_path(self):
        folder_path = utils.get_folder_path_from_file_path(self.tv_sort.settings.get('DUMMY_FILE_PATH'))
        self.assertEquals(self.tv_sort.settings.get('TV_PATH'), folder_path)
