import unittest

from tvsort import *


class TvSortTest(unittest.TestCase):
    def test_remove_file(self):
        self.assertTrue(remove_file(settings.test_file_path))

    def test_is_file_exists(self):
        self.assertFalse(is_file_exists(settings.test_file_path))
        create_test_file()
        self.assertTrue(is_file_exists(settings.test_file_path))

    def test_is_process_already_run(self):
        self.assertFalse(is_process_already_run(settings.dummy_file_path))

    def test_transform_to_path_name(self):
        original_text = 'This is a string with space.s and dots.'
        new_text = 'This.Is.A.String.With.Space.s.And.Dots.'
        self.assertEquals(transform_to_path_name(original_text), new_text)

    def test_replace_space_with_dots_int_input(self):
        string = 1
        self.assertEquals(transform_to_path_name(string), '1')

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
