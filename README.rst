.. image:: https://ci.appveyor.com/api/projects/status/1fec2l6od2qgyqvl?svg=true
    :target: https://ci.appveyor.com/project/shlomiLan/tvsort-sl
.. image:: https://badge.fury.io/py/tvsort_sl.svg
    :target: https://badge.fury.io/py/tvsort_sl
.. image:: https://codecov.io/gh/shlomiLan/tvsort_sl/branch/master/graph/badge.svg
    :target: https://codecov.io/gh/shlomiLan/tvsort_sl
.. image:: https://img.shields.io/github/downloads/shlomiLan/tvsort_sl/total.svg
    :target: https://img.shields.io/github/downloads/shlomiLan/tvsort_sl
.. image:: https://api.codacy.com/project/badge/Grade/af326adf8c2c4644b1b0e6df9c21016c
   :alt: Codacy Badge
   :target: https://www.codacy.com/app/shlomiLan/tvsort_sl?utm_source=github.com&utm_medium=referral&utm_content=shlomiLan/tvsort_sl&utm_campaign=badger
   
==================
tvsort_sl - test 2
==================

Sort Viedo files to TV-shows and Movies folders, after that Update KODI library and download subtitles for each viedo file.

Installation
------------
::

    pip install tvsort_sl

Config
------
-  Setup

    Update your settings in: `local.yaml`

    There set the following things:
        - BASE_DRIVE => drive letter or pc-name where the videos are localted, in this drive should be 3 sub-folders:
            - Unsortted => Folder with all the videos that needs to be sortted
            - TVShows => Folder to which each video that will be flag as tv-show will be moved
            - Movies => Folder to which each movie that will be flag as tv-show will be moved
        - KODI_IP (optional) => IP for the KODI device
        - MOVE_FILES => by default all files will be move (from Unsortted to TVShows OR Movies), if you want to keep the files in `Unsortted` folder you can change this settings to `False`

-  Run

    python tvsort_sl.py

- Error handling

    By defualt this program can run on more than 1 one process at the same time. If you try and run it and get the following error

    `Proses already running`

    it means that there is another process of this program that it already running and you should allow it to end firat.
    If you think that there isn't another process that is already running, it means that in the last time the process run it was stuck,
    so you can manually remove the 'dummy.txt' file from the 'TV_PATH' folder and than try again to run the process
