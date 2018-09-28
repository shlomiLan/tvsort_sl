import os

from tvsort_sl.conf import SETTINGS_FOLDER, get_conf_file_name
from tvsort_sl.tests.test_base import tv_sort
from tvsort_sl.utils import check_project_setup


def test_missing_conf_file():
    file_path = os.path.join(SETTINGS_FOLDER, 'test.yml')
    new_file_path = os.path.join(SETTINGS_FOLDER, 'test1.yml')
    os.rename(file_path, new_file_path)

    conf_files = get_conf_file_name(is_test=True)
    response = check_project_setup(tv_sort.settings, conf_files)
    assert response[0][0] == 'error'

    # clean-up
    os.rename(new_file_path, file_path)
