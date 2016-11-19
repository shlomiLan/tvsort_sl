import unittest

from tvsort import *


class TvSortTest(unittest.TestCase):
    def test_remove_file(self):
        self.assertFalse(remove_file(settings.test_file_path))

    def test_is_file_exists(self):
        self.assertFalse(is_file_exists(settings.test_file_path))
        create_test_file()
        self.assertTrue(is_file_exists(settings.test_file_path))
        remove_test_file(settings.test_file_path)

    def test_process_not_running(self):
        self.assertFalse(is_process_already_run(settings.dummy_file_path))

    def test_process_is_running(self):
        dummy_file_path = settings.dummy_file_path
        create_dummy_file(dummy_file_path)
        self.assertTrue(is_process_already_run(settings.dummy_file_path))
        delete_dummy_file(dummy_file_path)

    def test_transform_to_path_name(self):
        original_text = 'This is a string with space.s and dots.'
        new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
        self.assertEquals(transform_to_path_name(original_text), new_text)

    def test_replace_space_with_dots_int_input(self):
        string = 1
        self.assertEquals(transform_to_path_name(string), '1')

    def test_not_tv_show(self):
        file_name = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK'
        guess = guessit(file_name)
        self.assertFalse(is_tv_show(guess))

    def test_is_tv_show(self):
        file_name = 'Mr Robot S01E05 HDTV x264-KILLERS[ettv]'
        guess = guessit(file_name)
        self.assertTrue(is_tv_show(guess))

    def test_is_movie(self):
        file_name = 'San Andreas 2015 720p WEB-DL x264 AAC-JYK'
        guess = guessit(file_name)
        self.assertTrue(is_movie(guess))

    def test_main(self):
        main()
        pass

    def test_compressed_file(self):
        file_name = 'test.zip'
        self.assertTrue(is_compressed(file_name))

    def test_not_compressed_file(self):
        file_name = 'test.avi'
        self.assertFalse(is_compressed(file_name))

    def test_file_in_ext_list(self):
        self.assertTrue(is_file_ext_in_list('zip', settings.compress_exts))

    def test_file_not_in_ext_list(self):
        self.assertFalse(is_file_ext_in_list('avi', settings.compress_exts))

    def test_garbage_file(self):
        self.assertFalse(is_garbage_file('test.avi'))

    def test_media_file(self):
        self.assertTrue(is_media('test.avi'))

    def test_show_name(self):
        guess = guessit('Anger.Management.S01E01.720p.HDTV.x264-IMMERSE.mkv')
        show_name = get_show_name(guess)
        self.assertEquals(show_name, 'Anger Management')

    @staticmethod
    def test_copy_file():
        if not is_file_exists(settings.test_file_path):
            create_test_file()

        winshell.copy_file(settings.test_file_path, settings.tv_path,
                           allow_undo=True, no_confirm=False, rename_on_collision=True, silent=False, hWnd=None)
        winshell.delete_file(settings.test_file_path, allow_undo=True, no_confirm=True, silent=True, hWnd=None)
        winshell.delete_file(settings.test_file_path_in_tv, allow_undo=True, no_confirm=True, silent=True, hWnd=None)


def create_test_file():
    test_file = open(settings.test_file_path, 'w')
    test_file.close()


def remove_test_file(file_path):
    remove_file(file_path)