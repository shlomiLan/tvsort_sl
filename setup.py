from setuptools import setup


def long_description():
    with open('README.md', 'r', encoding='utf-8') as f:
        return f.read()


setup(
    name='tvsort_sl',
    packages=['tvsort_sl'],
    version='2.0.0',
    description='Sort movies and TV-shows files',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    author='Shlomi Lanton',
    author_email='shlomilanton@gmail.com',
    url='https://github.com/shlomiLan/tvsort_sl',
    download_url='https://github.com/shlomiLan/tvsort_sl/archive/0.1.zip',
    keywords=['sort', 'tv', 'show', 'movie', 'KODI', 'XBM1C'],
    classifiers=[],
    setup_requires=['wheel']
)
