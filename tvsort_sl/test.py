import os
import unittest

from guessit import guessit

import tvsort_sl as app_logic

from conf import settings


class TvSortTest(unittest.TestCase):
    logger = app_logic.create_logger()

    def test_is_file_exists(self):
        file_path = settings.TEST_FILE_PATH
        self.assertFalse(app_logic.is_file_exists(file_path))
        app_logic.create_file(file_path)
        self.assertTrue(app_logic.is_file_exists(file_path))
        app_logic.delete_file(file_path)

    def test_process_not_running(self):
        self.assertFalse(app_logic.is_process_already_run(settings.DUMMY_FILE_PATH))

    def test_process_is_running(self):
        dummy_file_path = settings.DUMMY_FILE_PATH
        app_logic.create_file(dummy_file_path)
        self.assertTrue(app_logic.is_process_already_run(settings.DUMMY_FILE_PATH))
        app_logic.delete_file(dummy_file_path)

    def test_transform_to_path_name(self):
        original_text = 'This is a string with space.s and dots.'
        new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
        self.assertEquals(app_logic.transform_to_path_name(original_text), new_text)

    def test_replace_space_with_dots_int_input(self):
        string = 1
        self.assertEquals(app_logic.transform_to_path_name(string), '1')

    def test_not_tv_show(self):
        file_name = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK'
        guess = guessit(file_name)
        self.assertFalse(app_logic.is_tv_show(guess))

    def test_is_tv_show(self):
        file_name = 'Mr Robot S01E05 HDTV x264-KILLERS[ettv]'
        guess = guessit(file_name)
        self.assertTrue(app_logic.is_tv_show(guess))

    def test_is_movie(self):
        file_name = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK'
        guess = guessit(file_name)
        self.assertTrue(app_logic.is_movie(guess))

    def test_compressed_file(self):
        file_name = 'test.zip'
        self.assertTrue(app_logic.is_compressed(file_name))

    def test_not_compressed_file(self):
        file_name = 'test.avi'
        self.assertFalse(app_logic.is_compressed(file_name))

    def test_file_in_ext_list(self):
        self.assertTrue(app_logic.is_file_ext_in_list('zip', settings.COMPRESS_EXTS))

    def test_file_not_in_ext_list(self):
        self.assertFalse(app_logic.is_file_ext_in_list('avi', settings.COMPRESS_EXTS))

    def test_garbage_file(self):
        self.assertFalse(app_logic.is_garbage_file('test.avi'))

    def test_media_file(self):
        self.assertTrue(app_logic.is_media('test.avi'))

    def test_show_name(self):
        guess = guessit('Anger.Management.S01E01.720p.HDTV.x264-IMMERSE.mkv')
        show_name = app_logic.get_show_name(guess)
        self.assertEquals(show_name, 'Anger Management')

    def test_empty_folder(self):
        folder_path = create_dummy_folder()
        self.assertTrue(app_logic.folder_empty(folder_path))
        os.rmdir(folder_path)

    def test_not_empty_folder(self):
        file_name = 'dummy1.txt'
        folder_path = create_dummy_folder()
        file_path = '{}\{}'.format(folder_path, file_name)
        app_logic.create_file(file_path)
        self.assertFalse(app_logic.folder_empty(folder_path))
        app_logic.delete_file(file_path)
        os.rmdir(folder_path)

    def test_wrong_series_name(self):
        guess = guessit('House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv')
        show_name = app_logic.get_show_name(guess)
        app_logic.add_missing_country(guess, show_name)
        self.assertEquals(guess.get('country'), 'US')

    def test_get_file_ext(self):
        file_name = 'House.of.Cards.2013.S04E01.720p.WEBRip.X264-DEFLATE.mkv'
        file_ext = app_logic.get_file_ext(file_name)
        self.assertEquals('mkv', file_ext)

    def test_delete_file(self):
        dummy_file_path = settings.DUMMY_FILE_PATH
        app_logic.create_file(dummy_file_path)
        self.assertTrue(app_logic.delete_file(dummy_file_path))

    def test_delete_file_fail(self):
        dummy_file_path = settings.DUMMY_FILE_PATH
        self.assertFalse(app_logic.delete_file(dummy_file_path))

    def test_move_file(self):
        test_file_path = settings.TEST_FILE_PATH
        app_logic.create_file(test_file_path)
        new_path = settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, app_logic.get_file_name(test_file_path))
        self.assertTrue(app_logic.copy_file(test_file_path, new_path, new_test_file_path))
        # Clean-up
        app_logic.delete_file(new_test_file_path)

    def test_copy_file(self):
        test_file_path = settings.TEST_FILE_PATH
        app_logic.create_file(test_file_path)
        new_path = settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, app_logic.get_file_name(test_file_path))
        self.assertTrue(app_logic.copy_file(test_file_path, new_path, new_test_file_path, move_file=False))
        # Delete both files
        app_logic.delete_file(test_file_path)
        app_logic.delete_file(new_test_file_path)

    def test_copy_file_fail(self):
        test_file_path = settings.TEST_FILE_PATH
        new_path = settings.TV_PATH
        new_test_file_path = '{}\{}'.format(new_path, app_logic.get_file_name(test_file_path))
        self.assertFalse(app_logic.copy_file(test_file_path, new_path, new_test_file_path))


def create_dummy_folder():
    base_path = settings.UNSORTED_PATH
    folder_name = 'dummy_folder'
    app_logic.create_folder(folder_name, base_path)
    return '{}\{}'.format(base_path, folder_name)
