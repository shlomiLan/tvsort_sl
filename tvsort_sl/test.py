# coding=utf-8
from __future__ import unicode_literals

import unittest

import mock as mock
from guessit import guessit

from tvsort_sl import TvSort


class TvSortTest(unittest.TestCase):
    tv_sort = TvSort(base_drive='c:')
    logger = tv_sort.create_logger()

    def setUp(self):
        self.tv_sort.create_folder(self.tv_sort.settings.TV_PATH)
        self.tv_sort.create_folder(self.tv_sort.settings.DUMMY_PATH)
        self.tv_sort.create_folder(self.tv_sort.settings.MOVIES_PATH)
        self.tv_sort.create_folder(self.tv_sort.settings.UNSORTED_PATH)

    # def tearDown(self):
    #     self.tv_sort.delete_folder(self.tv_sort.settings.TV_PATH)
    #     self.tv_sort.delete_folder(self.tv_sort.settings.DUMMY_PATH)
    #     self.tv_sort.delete_folder(self.tv_sort.settings.MOVIES_PATH)
    #     self.tv_sort.delete_folder(self.tv_sort.settings.UNSORTED_PATH)

    # @mock.patch('tvsort_sl.is_process_already_running', return_value=True)
    # def test_main(self):
    #     test_file_name = self.tv_sort.settings.TEST_ZIP_name
    #     test_file_path = '{}\{}'.format(self.tv_sort.settings.TEST_FILES, test_file_name)
    #     new_test_file_folder = self.tv_sort.settings.UNSORTED_PATH
    #     new_test_file_path = '{}\{}'.format(new_test_file_folder, test_file_name)
    #     self.tv_sort.copy_file(test_file_path, new_test_file_folder, None, move_file=False)
    #     # self.assertTrue(self.tv_sort.run())
    #     print(new_test_file_path)
    #     self.tv_sort.delete_file(new_test_file_path)

    def test_is_file_exists(self):
        file_path = self.tv_sort.settings.TEST_FILE_PATH
        self.assertFalse(self.tv_sort.is_file_exists(file_path))
        self.tv_sort.create_file(file_path)
        self.assertTrue(self.tv_sort.is_file_exists(file_path))
        self.tv_sort.delete_file(file_path)

    def test_process_not_running(self):
        self.assertFalse(self.tv_sort.is_process_already_running(self.tv_sort.settings.DUMMY_FILE_PATH))

    def test_process_is_running(self):
        dummy_file_path = self.tv_sort.settings.DUMMY_FILE_PATH
        self.tv_sort.create_file(dummy_file_path)
        self.assertTrue(self.tv_sort.is_process_already_running(self.tv_sort.settings.DUMMY_FILE_PATH))
        self.tv_sort.delete_file(dummy_file_path)

    def test_transform_to_path_name(self):
        original_text = 'This is a string with space.s and dots.'
        new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
        self.assertEquals(self.tv_sort.transform_to_path_name(original_text), new_text)

    def test_replace_space_with_dots_int_input(self):
        string = 1
        self.assertEquals(self.tv_sort.transform_to_path_name(string), '1')

    def test_not_tv_show(self):
        file_name = str('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
        guess = guessit(file_name)
        self.assertFalse(self.tv_sort.is_tv_show(guess))

    def test_is_tv_show(self):
        file_name = str('Mr Robot S01E05 HDTV x264-KILLERS[ettv]')
        guess = guessit(file_name)
        self.assertTrue(self.tv_sort.is_tv_show(guess))

    def test_is_movie(self):
        file_name = str('San Andreas 2015 720p WEB-DL x264 AAC-JYK')
        guess = guessit(file_name)
        self.assertTrue(self.tv_sort.is_movie(guess))

    def test_compressed_file(self):
        file_name = 'test.zip'
        self.assertTrue(self.tv_sort.is_compressed(file_name))

    def test_not_compressed_file(self):
        file_name = 'test.avi'
        self.assertFalse(self.tv_sort.is_compressed(file_name))

    def test_file_in_ext_list(self):
        self.assertTrue(self.tv_sort.is_file_ext_in_list('zip', self.tv_sort.settings.COMPRESS_EXTS))

    def test_file_not_in_ext_list(self):
        self.assertFalse(self.tv_sort.is_file_ext_in_list('avi', self.tv_sort.settings.COMPRESS_EXTS))

    def test_garbage_file(self):
        self.assertFalse(self.tv_sort.is_garbage_file('test.avi'))

    def test_media_file(self):
        self.assertTrue(self.tv_sort.is_media('test.avi'))

    def test_show_name(self):
        guess = guessit(str('Anger.Management.S01E01.720p.HDTV.x264-IMMERSE.mkv'))
        show_name = self.tv_sort.get_show_name(guess)
        self.assertEquals(show_name, 'Anger Management')

    def test_folder_exist(self):
        folder_path = self.tv_sort.settings.FAKE_PATH
        self.assertFalse(self.tv_sort.is_folder_exists(folder_path))
        self.assertFalse(self.tv_sort.delete_folder(folder_path))
        folder_path = self.tv_sort.settings.TV_PATH
        self.assertTrue(self.tv_sort.is_folder_exists(folder_path))

    def test_delete_folder(self):
        self.assertTrue(self.tv_sort.delete_folder(self.tv_sort.settings.UNSORTED_PATH))
        self.tv_sort.create_folder(self.tv_sort.settings.UNSORTED_PATH)

    def test_empty_folder(self):
        folder_path = self.tv_sort.settings.DUMMY_PATH
        self.assertTrue(self.tv_sort.folder_empty(folder_path))

    def test_not_empty_folder(self):
        file_name = 'dummy1.txt'
        folder_path = self.tv_sort.settings.DUMMY_PATH
        file_path = '{}\{}'.format(folder_path, file_name)
        self.tv_sort.create_file(file_path)
        self.assertFalse(self.tv_sort.folder_empty(folder_path))
        self.assertFalse(self.tv_sort.delete_folder(folder_path))
        self.tv_sort.delete_file(file_path)

    def test_wrong_series_name(self):
        guess = guessit(str('House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'))
        show_name = self.tv_sort.get_show_name(guess)
        self.tv_sort.add_missing_country(guess, show_name)
        self.assertEquals(guess.get('country'), 'US')

    def test_wrong_country_data_in_series_name(self):
        guess = guessit(str('This.is.Us.S01E01.HDTV.x264-KILLERS.mkv'))
        self.tv_sort.remove_wrong_country_data(guess)
        self.assertEquals(guess.get('country'), None)

    def test_get_file_ext(self):
        file_name = 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'
        file_ext = self.tv_sort.get_file_ext(file_name)
        self.assertEquals('mkv', file_ext)

    def test_delete_file(self):
        dummy_file_path = self.tv_sort.settings.DUMMY_FILE_PATH
        self.tv_sort.create_file(dummy_file_path)
        self.assertTrue(self.tv_sort.delete_file(dummy_file_path))

    def test_delete_file_fail(self):
        dummy_file_path = self.tv_sort.settings.DUMMY_FILE_PATH
        self.assertFalse(self.tv_sort.delete_file(dummy_file_path))

    def test_move_file(self):
        test_file_path = self.tv_sort.settings.TEST_FILE_PATH
        self.tv_sort.create_file(test_file_path)
        new_path = self.tv_sort.settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, self.tv_sort.get_file_name(test_file_path))
        self.assertTrue(self.tv_sort.copy_file(test_file_path, new_path, new_test_file_path))
        # Clean-up
        self.tv_sort.delete_file(new_test_file_path)

    def test_copy_file(self):
        test_file_path = self.tv_sort.settings.TEST_FILE_PATH
        self.tv_sort.create_file(test_file_path)
        new_path = self.tv_sort.settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, self.tv_sort.get_file_name(test_file_path))
        self.assertTrue(self.tv_sort.copy_file(test_file_path, new_path, new_test_file_path, move_file=False))
        # Delete both files
        self.tv_sort.delete_file(test_file_path)
        self.tv_sort.delete_file(new_test_file_path)

    def test_copy_file_fail(self):
        test_file_path = self.tv_sort.settings.TEST_FILE_PATH
        new_path = self.tv_sort.settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, self.tv_sort.get_file_name(test_file_path))
        self.assertFalse(self.tv_sort.copy_file(test_file_path, new_path, new_test_file_path))

    def test_get_folder_name_from_path(self):
        folder_path = self.tv_sort.get_folder_path_from_file_path(self.tv_sort.settings.DUMMY_FILE_PATH)
        self.assertEquals(self.tv_sort.settings.TV_PATH, folder_path)
