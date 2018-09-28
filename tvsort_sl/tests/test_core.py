import os

import mock
from guessit import guessit

import tvsort_sl.utils as utils
from tvsort_sl.conf import check_project_setup, get_conf_file_name
from tvsort_sl.tests.test_base import tv_sort


def setup_function(_):
    utils.create_folder(tv_sort.settings.get('TV_PATH'))
    utils.create_folder(tv_sort.settings.get('DUMMY_PATH'))
    utils.create_folder(tv_sort.settings.get('MOVIES_PATH'))
    utils.create_folder(tv_sort.settings.get('UNSORTED_PATH'))


def teardown_function(_):
    utils.delete_folder(tv_sort.settings.get('TV_PATH'), force=True)
    utils.delete_folder(tv_sort.settings.get('DUMMY_PATH'), force=True)
    utils.delete_folder(tv_sort.settings.get('MOVIES_PATH'), force=True)
    utils.delete_folder(tv_sort.settings.get('UNSORTED_PATH'), force=True)


@mock.patch('requests.post', return_value={'status_code': 200})
def test_main(_):
    new_files_folder = tv_sort.settings.get('UNSORTED_PATH')

    # Add ZIP file
    zip_file_path = tv_sort.settings.get('TEST_ZIP_PATH')
    response = utils.copy_file(zip_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'

    # Add garbage file
    garbage_file_path = tv_sort.settings.get('TEST_GARBAGE_PATH')
    response = utils.copy_file(garbage_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'

    # Add tv-show files
    tv_file_path = tv_sort.settings.get('TEST_TV_PATH')
    response = utils.copy_file(tv_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'
    tv_file_path = tv_sort.settings.get('TEST_TV_2_PATH')
    response = utils.copy_file(tv_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'
    tv_file_path = tv_sort.settings.get('TEST_TV_3_PATH')
    response = utils.copy_file(tv_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'

    # Add movie file
    movie_file_path = tv_sort.settings.get('TEST_MOVIE')
    response = utils.copy_file(movie_file_path, new_files_folder, move_file=False)
    assert response[0][0] == 'info'

    # create empty folder
    response = utils.create_folder(tv_sort.settings.get('TEST_FOLDER_IN_UNSORTED'))
    assert response[0][0] == 'info'

    result = tv_sort.run()
    counters = result.get('counters')
    assert counters.get('move_or_copy') == 4
    assert counters.get('delete') == 3


@mock.patch('requests.post', return_value={'status_code': 200})
def test_main_process_running(_):
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    utils.create_file(dummy_file_path)
    result = tv_sort.run()
    assert 'Proses already running' in result.get('errors')
    response = utils.delete_file(dummy_file_path)
    assert response[0][0] == 'info'


@mock.patch('requests.post', return_value={'status_code': 200})
def test_update_xbmc(_):
    response = utils.update_xbmc(tv_sort.settings.get('KODI_IP'))
    assert response[0][0] == 'info'


@mock.patch('tvsort_sl.utils.is_folder_exists', return_value=False)
def test_no_logs_folder(_):
    conf_files = get_conf_file_name(is_test=True)
    response = check_project_setup(tv_sort.settings, conf_files)
    assert response[0][0] == 'error'


def test_is_file_exists():
    file_path = tv_sort.settings.get('TEST_FILE_PATH')
    assert not utils.is_file_exists(file_path)
    response = utils.create_file(file_path)
    assert response[0][0] == 'info'
    assert 'File was created' in response[0][1]

    assert utils.is_file_exists(file_path)
    response = utils.delete_file(file_path)
    assert response[0][0] == 'info'


def test_replace_space_with_dots_int_input():
    string = 1
    assert utils.transform_to_path_name(string) == '1'


def test_not_tv_show():
    tv_file_name = tv_sort.settings.get('TEST_MOVIE')
    video = guessit(tv_file_name)
    assert not utils.is_tv_show(video)


def test_is_tv_show():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = guessit(tv_file_name)
    assert utils.is_tv_show(video)


def test_is_movie():
    tv_file_name = tv_sort.settings.get('TEST_MOVIE')
    video = guessit(tv_file_name)
    assert utils.is_movie(video)


def test_compressed_file():
    file_name = 'test.zip'
    assert utils.is_compressed(file_name, tv_sort.settings.get('EXTENSIONS'))


def test_not_compressed_file():
    file_name = 'test.avi'
    assert not utils.is_compressed(file_name, tv_sort.settings.get('EXTENSIONS'))


def test_file_in_ext_list():
    assert utils.is_file_ext_in_list('zip', tv_sort.extensions.get('COMPRESS'))


def test_file_not_in_ext_list():
    assert not utils.is_file_ext_in_list('avi', tv_sort.extensions.get('COMPRESS'))


def test_garbage_file():
    assert utils.is_garbage_file('.DS_Store', tv_sort.extensions)
    assert not utils.is_garbage_file('test.avi', tv_sort.extensions)


def test_show_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = guessit(tv_file_name)
    show_name = utils.get_show_name(video)
    assert show_name == 'House of Cards'


def test_folder_exist():
    folder_path = tv_sort.settings.get('FAKE_PATH')
    assert not utils.is_folder_exists(folder_path)
    response = utils.delete_folder(folder_path)
    assert response[0][0] == 'error'

    folder_path = tv_sort.settings.get('TV_PATH')
    assert utils.is_folder_exists(folder_path)


def test_delete_folder():
    response = utils.delete_folder(tv_sort.settings.get('UNSORTED_PATH'))
    assert response[0][0] == 'info'

    response = utils.create_folder(tv_sort.settings.get('UNSORTED_PATH'))
    assert response[0][0] == 'info'


def test_create_folder():
    response = utils.delete_folder(tv_sort.settings.get('DUMMY_PATH'))
    assert response[0][0] == 'info'

    response = utils.create_folder(tv_sort.settings.get('DUMMY_PATH'))
    assert response[0][0] == 'info'


def test_create_folder_that_already_exists():
    response = utils.create_folder(tv_sort.settings.get('DUMMY_PATH'))
    assert response is None


def test_empty_folder():
    folder_path = tv_sort.settings.get('DUMMY_PATH')
    assert utils.folder_empty(folder_path)


def test_not_empty_folder():
    file_name = 'dummy1.txt'
    folder_path = tv_sort.settings.get('DUMMY_PATH')
    file_path = os.path.join(folder_path, file_name)
    response = utils.create_file(file_path)
    assert response[0][0] == 'info'
    assert not utils.folder_empty(folder_path)

    # Can't delete not empty folder
    response = utils.delete_folder(folder_path)
    assert all(message[0] == 'error' for message in response)

    response = utils.delete_file(file_path)
    assert response[0][0] == 'info'


def test_wrong_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    video = guessit(tv_file_name)
    show_name = utils.transform_to_path_name(utils.get_show_name(video))
    utils.add_missing_country(video, show_name)
    assert video.get('country') == 'US'


def test_good_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_3_PATH')
    video = guessit(tv_file_name)
    show_name = utils.transform_to_path_name(utils.get_show_name(video))
    assert show_name == 'This.Is.Us'


def test_wrong_country_data_in_series_name():
    tv_file_name = tv_sort.settings.get('TEST_TV_3_PATH')
    video = guessit(tv_file_name)
    assert video.get('country') is None


def test_get_file_ext():
    tv_file_name = tv_sort.settings.get('TEST_TV_PATH')
    file_ext = utils.get_file_ext(tv_file_name)
    assert 'mkv' == file_ext


def test_delete_file():
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    response = utils.create_file(dummy_file_path)
    assert response[0][0] == 'info'

    response = utils.delete_file(dummy_file_path)
    assert response[0][0] == 'info'


def test_delete_file_fail():
    dummy_file_path = tv_sort.settings.get('DUMMY_FILE_PATH')
    response = utils.delete_file(dummy_file_path)
    assert response[0][0] == 'error'
    assert 'Unexpected error:' in response[0][1]


def test_move_file():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    utils.create_file(test_file_path)
    new_path = tv_sort.settings.get('TV_PATH')
    new_test_file_path = os.path.join(new_path, utils.get_file_name(test_file_path))

    response = utils.copy_file(test_file_path, new_path)
    assert response[0][0] == 'info'

    # Clean-up
    response = utils.delete_file(new_test_file_path)
    assert response[0][0] == 'info'


def test_move_file_already_exists():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    new_path = tv_sort.settings.get('TV_PATH')
    new_test_file_path = os.path.join(new_path, utils.get_file_name(test_file_path))

    response = utils.create_file(test_file_path)
    assert response[0][0] == 'info'
    response = utils.copy_file(test_file_path, new_path, move_file=False)
    assert response[0][0] == 'info'

    response = utils.create_file(test_file_path)
    assert response[0][0] == 'info'
    response = utils.copy_file(test_file_path, new_path)
    tv_sort.logger.error(response)
    assert response[0][0] == 'error'

    # Clean-up
    response = utils.delete_file(new_test_file_path)
    assert response[0][0] == 'info'


def test_copy_file():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    utils.create_file(test_file_path)
    new_path = tv_sort.settings.get('TV_PATH')
    new_test_file_path = os.path.join(new_path, utils.get_file_name(test_file_path))
    response = utils.copy_file(test_file_path, new_path, move_file=False)
    assert response[0][0] == 'info'

    # Delete both files
    response = utils.delete_file(test_file_path)
    assert response[0][0] == 'info'
    response = utils.delete_file(new_test_file_path)
    assert response[0][0] == 'info'


def test_copy_file_fail():
    test_file_path = tv_sort.settings.get('TEST_FILE_PATH')
    new_path = tv_sort.settings.get('TV_PATH')
    response = utils.copy_file(test_file_path, new_path)
    assert response[0][0] == 'error'


def test_get_folder_name_from_path():
    folder_path = utils.get_folder_path_from_file_path(tv_sort.settings.get('DUMMY_FILE_PATH'))
    assert tv_sort.settings.get('TV_PATH') == folder_path


def test_transform_to_path_name():
    original_text = 'This is a string with space.s and dots.'
    new_text = 'This.Is.A.String.With.Space.S.And.Dots.'
    assert utils.transform_to_path_name(original_text) == new_text
