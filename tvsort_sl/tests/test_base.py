import logging

from tvsort_sl.app import TvSort

is_test = True
tv_sort = TvSort(is_test=is_test, log_level=logging.INFO)
