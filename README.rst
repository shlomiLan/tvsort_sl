.. image:: https://ci.appveyor.com/api/projects/status/1fec2l6od2qgyqvl?svg=true
	:target: https://ci.appveyor.com/project/shlomiLan/tvsort-sl
.. image:: https://badge.fury.io/py/tvsort_sl.svg
	:target: https://badge.fury.io/py/tvsort_sl
.. image:: https://codecov.io/gh/shlomiLan/tvsort_sl/branch/master/graph/badge.svg
	:target: https://codecov.io/gh/shlomiLan/tvsort_sl
.. image:: https://img.shields.io/github/downloads/shlomiLan/tvsort_sl/total.svg
	:target: https://img.shields.io/github/downloads/shlomiLan/tvsort_sl

=========
tvsort_sl
=========

Sort files to TV-shows and Movies folders and than (optional) update the KODI library

Installation
------------
::

	pip install tvsort_sl

Config
------
-  Setup

	First you need to set the path of the main 3 folders and the KODI IP (if needed):
		- TV_PATH => folder for all TV-Shows, each show will be in a separate folder
		- MOVIES_PATH => folder for all NON TV-Shows files, all files will be in the same directory
		- UNSORTED_PATH => origin folder that contains all files that needs to be sorted
		- KODI_IP (optional) => IP for the KODI device

-  Run

	python tvsort_sl.py

- Error handling

	If you get this error message:
	::
		Proses already running
	and you are sure that there isn't another process already running, it means that in the last time the process run it was stuck,
	so you can manually remove the 'dummy.txt' file from the 'TV_PATH' folder and than try again to run the process
