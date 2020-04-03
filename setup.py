from setuptools import setup, find_packages
import subprocess
import os
from pathlib import Path

dir_ = Path(__file__).parent

def subprocess_cmd(*commands, decode=True):
    cmdstr = ''
    for c in commands:
        cmdstr += (c + ' && ')
    cmdstr = cmdstr.strip(' &&')
    process = subprocess.Popen(cmdstr, stdout=subprocess.PIPE, shell=True)
    ret = process.communicate()[0]
    if (decode):
        ret = ret.decode('utf-8')
    return ret

subprocess_cmd('pip install -r {}'.format(dir_ / "requirements.txt"))

setup(
    name='noaahistory',
    description='dev package',
    author='rlyon14',
    author_email='rlyon14@yahoo.com',
    version='0.1.1',
    packages=['noaahistory',],
    url="https://github.com/rlyon14/noaahistory",
    install_requires=(
    ),
    entry_points='''
        [console_scripts]
        weather=noaahistory.cli:cli
    ''',
)