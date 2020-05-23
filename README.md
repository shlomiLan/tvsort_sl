[![PyPI version](https://badge.fury.io/py/tvsort-sl.svg)](https://badge.fury.io/py/tvsort-sl)
[![codecov](https://codecov.io/gh/shlomiLan/tvsort_sl/branch/master/graph/badge.svg)](https://codecov.io/gh/shlomiLan/tvsort_sl)
![](https://img.shields.io/github/downloads/shlomiLan/tvsort_sl/total.svg)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/d3353839b44e4a3d9d09815f40c92616)](https://www.codacy.com/app/public/tvsort_sl?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=shlomiLan/tvsort_sl&amp;utm_campaign=Badge_Grade)

# Tvsort_sl

Sort Video files to TV-shows and Movies folders and update local KODI library.

### Prerequisites

The program will take files from `unsorted` folder and move one of the following folders: `TVShows`, `Movies`, so you need to create them.

### Deployment

```
pip install virtualenv
virtualenv venv
source ./venv/bin/activate
pip install -r dev.txt
mkdir logs
```

### Usage
```
pip install tvsort_sl 
```

Update `local.yml` in `tvsort_sl/tvsort_sl/settings` with the following:
* `KODI_IP`: IP of the Kodi server
* `BASE_DRIVE`: Drive letter or name in network where content folders (`unsorted`, `TVShows` etc.) can be found.

```
cd tvsort_sl
python -m tvsort_sl.app
```

## Running the tests

* Tests: `pytest`
* Coverage: `coverage run -m pytest`

Those are only unit-tests that test the code functionality and ability to move files.

## Configuration:
In `conf.yaml` the `MOVE_FILES` flag is used to determine if files should be move or copy. 

## Contributing

Please read [contributing.md] for details on our code of conduct, and the process for submitting pull requests to us.

## Authors

* **Shlomi Lan** - *Initial work* - [shlomiLan](https://github.com/shlomiLan)

See also the list of contributors who participated in this project.

## License

see the license.txt for details
