from setuptools import setup, find_packages

setup(
    name='nws-history',
    description='dev package',
    author='rlyon',
    author_email='rlyon14@yahoo.com',
    version='0.1.1',
    packages=['nws-history',],
    install_requires=(
		'matplotlib>=3.1.0',
        'numpy',
        'mpl-marker',
        'click',
        'pyqt5'
    ),
    entry_points='''
        [console_scripts]
        weather=cli:cli
    ''',
)