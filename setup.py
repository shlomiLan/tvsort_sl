from distutils.core import setup
setup(
    name='tvsort_sl',
    packages=['tvsort_sl'],
    install_requires=['requests', 'winshell', 'guessit', 'opster', 'patool'],
    version='0.2',
    description='Sort movies and TV-shows files',
    author='Shlomi Lanton',
    author_email='shlomilanton@gmail.com',
    url='https://github.com/shlomiLan/tvsort_sl',
    download_url='https://github.com/shlomiLan/tvsort_sl/archive/0.1.zip',
    keywords=['sort', 'tv', 'show', 'movie', 'KODI', 'XBMC'],
    classifiers=[],
)
