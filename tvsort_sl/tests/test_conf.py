import os

from tvsort_sl.tests.test_base import tv_sort


def test_is_file_exists():
    file_path = os.path.join(tv_sort.settings_folder, 'test.yml')
    new_file_path = os.path.join(tv_sort.settings_folder, 'test1.yml')
    os.rename(file_path, new_file_path)
    response = tv_sort.check_project_setup(True)
    assert response[0][0] == 'error'

    # clean-up
    os.rename(new_file_path, file_path)
