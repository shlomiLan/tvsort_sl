# coding=utf-8
from __future__ import unicode_literals

import os

import pytest
from mock import mock

import tvsort_sl.utils as utils
from .test_base import tv_sort, is_test


def setup_function(_):
    utils.create_folder(tv_sort.settings.get('TV_PATH'), tv_sort.logger)
    utils.create_folder(tv_sort.settings.get('DUMMY_PATH'), tv_sort.logger)
    utils.create_folder(tv_sort.settings.get('MOVIES_PATH'), tv_sort.logger)
    utils.create_folder(tv_sort.settings.get('UNSORTED_PATH'), tv_sort.logger)


def teardown_function(_):
    utils.delete_folder(tv_sort.settings.get('TV_PATH'), tv_sort.logger, force=True)
    utils.delete_folder(tv_sort.settings.get('DUMMY_PATH'), tv_sort.logger, force=True)
    utils.delete_folder(tv_sort.settings.get('MOVIES_PATH'), tv_sort.logger, force=True)
    utils.delete_folder(tv_sort.settings.get('UNSORTED_PATH'), tv_sort.logger, force=True)


@mock.patch('requests.post', return_value={'status_code': 200})
# TODO: fix this test, can run without any files
def test_main(_):
    new_files_folder = tv_sort.settings.get('UNSORTED_PATH')

    # Add ZIP file
    zip_file_path = tv_sort.settings.get('TEST_ZIP_PATH')
    utils.copy_file(zip_file_path, new_files_folder, tv_sort.logger, move_file=False)

    # Add garbage file
    garbage_file_path = tv_sort.settings.get('TEST_GARBAGE_PATH')
    utils.copy_file(garbage_file_path, new_files_folder, tv_sort.logger, move_file=False)

    # Add tv-show files
    tv_file_path = tv_sort.settings.get('TEST_TV_PATH')
    utils.copy_file(tv_file_path, new_files_folder, tv_sort.logger, move_file=False)
    tv_file_path = tv_sort.settings.get('TEST_TV_2_PATH')
    utils.copy_file(tv_file_path, new_files_folder, tv_sort.logger, move_file=False)
    tv_file_path = tv_sort.settings.get('TEST_TV_3_PATH')
    utils.copy_file(tv_file_path, new_files_folder, tv_sort.logger, move_file=False)

    # Add movie file
    movie_file_path = tv_sort.settings.get('TEST_MOVIE')
    utils.copy_file(movie_file_path, new_files_folder, tv_sort.logger, move_file=False)

    # create empty folder
    utils.create_folder(tv_sort.settings.get('TEST_FOLDER_IN_UNSORTED'), tv_sort.logger)

    assert tv_sort.run()


@mock.patch('requests.post', return_value={'status_code': 200})
def test_main_process_running(_):
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    utils.create_file(dummy_file_path)
    assert not tv_sort.run()
    utils.delete_file(dummy_file_path, tv_sort.logger)


@mock.patch('requests.post', return_value={'status_code': 200})
def test_update_xbmc(_):
    utils.update_xbmc(tv_sort.settings.get('KODI_IP'), tv_sort.logger)


@mock.patch('tvsort_sl.utils.is_folder_exists', return_value=False)
def test_no_logs_folder(_):
    with pytest.raises(Exception):
        tv_sort.check_project_setup(is_test)


def test_is_file_exists():
    file_path = tv_sort.settings.get('TEST_FILE_PATH')
    assert not utils.is_file_exists(file_path)
    utils.create_file(file_path)
    assert utils.is_file_exists(file_path)
    utils.delete_file(file_path, tv_sort.logger)


def test_replace_space_with_dots_int_input():
    string = 1
    assert utils.transform_to_path_name(string) == '1'


def test_not_tv_show():
    tv_file_name = tv_sort.settings.get('TEST_MOVIE')
    video = utils.scan_video(tv_file_name)
    assert not utils.is_tv_show(video)


def test_is_tv_show():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = utils.scan_video(tv_file_name)
    assert utils.is_tv_show(video)


def test_is_movie():
    tv_file_name = tv_sort.settings.get('TEST_MOVIE')
    video = utils.scan_video(tv_file_name)
    assert utils.is_movie(video)


def test_compressed_file():
    file_name = 'test.zip'
    assert utils.is_compressed(file_name, tv_sort.settings)


def test_not_compressed_file():
    file_name = 'test.avi'
    assert not utils.is_compressed(file_name, tv_sort.settings)


def test_file_in_ext_list():
    assert utils.is_file_ext_in_list('zip', tv_sort.settings.get('COMPRESS_EXTS'))


def test_file_not_in_ext_list():
    assert not utils.is_file_ext_in_list('avi', tv_sort.settings.get('COMPRESS_EXTS'))


def test_garbage_file():
    assert not utils.is_garbage_file('test.avi', tv_sort.settings)


def test_show_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = utils.scan_video(tv_file_name)
    show_name = utils.get_show_name(video)
    assert show_name == 'House of Cards'


def test_folder_exist():
    folder_path = tv_sort.settings.get('FAKE_PATH')
    assert not utils.is_folder_exists(folder_path)
    assert not utils.delete_folder(folder_path, tv_sort.logger)
    folder_path = tv_sort.settings.get('TV_PATH')
    assert utils.is_folder_exists(folder_path)


def test_delete_folder():
    assert utils.delete_folder(tv_sort.settings.get('UNSORTED_PATH'), tv_sort.logger)
    utils.create_folder(tv_sort.settings.get('UNSORTED_PATH'), tv_sort.logger)


def test_create_folder():
    utils.delete_folder(tv_sort.settings.get('DUMMY_PATH'), tv_sort.logger)
    assert utils.create_folder(tv_sort.settings.get('DUMMY_PATH'), tv_sort.logger)


def test_create_folder_that_already_exists():
    assert utils.create_folder(tv_sort.settings.get('DUMMY_PATH'), tv_sort.logger)


def test_empty_folder():
    folder_path = tv_sort.settings.get('DUMMY_PATH')
    assert utils.folder_empty(folder_path)


def test_not_empty_folder():
    file_name = 'dummy1.txt'
    folder_path = tv_sort.settings.get('DUMMY_PATH')
    file_path = os.path.join(folder_path, file_name)
    utils.create_file(file_path)
    assert not utils.folder_empty(folder_path)
    assert not utils.delete_folder(folder_path, tv_sort.logger)
    utils.delete_file(file_path, tv_sort.logger)


def test_wrong_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = utils.scan_video(tv_file_name)
    show_name = utils.transform_to_path_name(utils.get_show_name(video))
    utils.add_missing_country(video, show_name)
    assert video.country == 'US'


def test_good_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_3_PATH')
    video = utils.scan_video(tv_file_name)
    show_name = utils.transform_to_path_name(utils.get_show_name(video))
    assert show_name == 'This.Is.Us'


def test_wrong_country_data_in_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_3_PATH')
    video = utils.scan_video(tv_file_name)
    utils.remove_wrong_country_data(video)
    assert video.country is None


def test_get_file_ext():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    file_ext = utils.get_file_ext(tv_file_name)
    assert 'mkv' == file_ext


def test_delete_file():
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    utils.create_file(dummy_file_path)
    assert utils.delete_file(dummy_file_path, tv_sort.logger)


def test_delete_file_fail():
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    assert not utils.delete_file(dummy_file_path, tv_sort.logger)


def test_move_file():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    utils.create_file(test_file_path)
    new_path = tv_sort.settings.get('TV_PATH')
    new_test_file_path = os.path.join(new_path, utils.get_file_name(test_file_path))
    assert utils.copy_file(test_file_path, new_path, tv_sort.logger)
    # Clean-up
    utils.delete_file(new_test_file_path, tv_sort.logger)


def test_copy_file():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    utils.create_file(test_file_path)
    new_path = tv_sort.settings.get('TV_PATH')
    new_test_file_path = os.path.join(new_path, utils.get_file_name(test_file_path))
    assert utils.copy_file(test_file_path, new_path, tv_sort.logger, move_file=False)
    # Delete both files
    utils.delete_file(test_file_path, tv_sort.logger)
    utils.delete_file(new_test_file_path, tv_sort.logger)


def test_copy_file_fail():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    new_path = tv_sort.settings.get('TV_PATH')
    assert not utils.copy_file(test_file_path, new_path, tv_sort.logger)


def test_get_folder_name_from_path():
    folder_path = utils.get_folder_path_from_file_path(tv_sort.settings.get('DUMMY_FILE_PATH'))
    assert tv_sort.settings.get('TV_PATH') == folder_path


def test_transform_to_path_name():
    original_text = 'This is a string with space.s and dots.'
    new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
    assert utils.transform_to_path_name(original_text) == new_text
