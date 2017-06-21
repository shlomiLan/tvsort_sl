import os
import unittest

import winshell
from guessit import guessit

import tvsort as app_logic

from conf import settings


class TvSortTest(unittest.TestCase):
    def test_is_file_exists(self):
        file_path = settings.test_file_path
        self.assertFalse(app_logic.is_file_exists(file_path))
        app_logic.create_file(file_path)
        self.assertTrue(app_logic.is_file_exists(file_path))
        winshell.delete_file(file_path, no_confirm=True)

    def test_process_not_running(self):
        self.assertFalse(app_logic.is_process_already_run(settings.dummy_file_path))

    def test_process_is_running(self):
        dummy_file_path = settings.dummy_file_path
        app_logic.create_file(dummy_file_path)
        self.assertTrue(app_logic.is_process_already_run(settings.dummy_file_path))
        winshell.delete_file(dummy_file_path, no_confirm=True)

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
        self.assertTrue(app_logic.is_file_ext_in_list('zip', settings.compress_exts))

    def test_file_not_in_ext_list(self):
        self.assertFalse(app_logic.is_file_ext_in_list('avi', settings.compress_exts))

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
        winshell.delete_file(file_path, no_confirm=True)
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

    @staticmethod
    def test_copy_file():
        file_path = settings.test_file_path
        if not app_logic.is_file_exists(file_path):
            app_logic.create_file(file_path)

        winshell.copy_file(file_path, settings.tv_path,
                           allow_undo=True, no_confirm=False, rename_on_collision=True, silent=False, hWnd=None)
        winshell.delete_file(file_path, allow_undo=True, no_confirm=True, silent=True, hWnd=None)
        winshell.delete_file(settings.test_file_path_in_tv, allow_undo=True, no_confirm=True, silent=True, hWnd=None)


def create_dummy_folder():
    base_path = settings.unsorted_path
    folder_name = 'dummy_folder'
    app_logic.create_folder(folder_name, base_path)
    return '{}\{}'.format(base_path, folder_name)
