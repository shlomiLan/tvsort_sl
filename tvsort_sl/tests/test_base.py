# coding=utf-8
from __future__ import unicode_literals

import logging

from tvsort_sl.tvsort_sl import TvSort

is_test = True
tv_sort = TvSort(is_test=is_test, log_level=logging.INFO)
