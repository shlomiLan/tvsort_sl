from setuptools import setup

setup(
    version='0.1.8',
    name="tvsort",
    packages = ['tvsort'],
    description='Sort TV episodes and Movies',
    author='Shlomi Lanton',
    package_dir={'tvsort': 'tvsort'},
    entry_points={
        'console_scripts': [
            'tvsort = tvsort.tvsort:main.command',
        ],
    },
    install_requires = [
        'opster',
        'guessit==2.1',
        'winshell',
        'patool',
        'kodi-json'
    ],
    extras_require={
        'win32': 'pywin32'
    },
)
