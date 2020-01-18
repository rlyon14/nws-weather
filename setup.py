from setuptools import setup, find_packages

setup(
    name='weather',
    description='dev package',
    author='Rick Lyon',
    author_email='rlyon@firstrf.com',
    version='0.1.1',
    packages=['weather',],
    install_requires=(
		'matplotlib>=3.1.0',
        'numpy',
        'markerplot',
        'click'
    ),
    entry_points='''
        [console_scripts]
        weather=cli:cli
    ''',
)