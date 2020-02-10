from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess
import os
from pathlib import Path

git_dependencies = [('markerplot', 'svn+https://github.com/rlyon14/markerplot/trunk#egg=markerplot'),]

dir_ = Path(__file__).parent
import_path = str(dir_ / 'cli')

class PostInstallCommand(install):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.installed_dp = False

    def run(self):
        super().run()
        self.installed_dp = True
        try:
            self.install_pkgs(*git_dependencies, editable=True)
        except:
            self.installed_dp = False

    def finalize_options(self):
        super().finalize_options()
        if (not self.installed_dp):
            self.install_pkgs(*git_dependencies, editable=True)
        
    def subprocess_cmd(self, *commands, decode = True):
        cmdstr = ''
        for c in commands:
            cmdstr += (c + ' && ')
        cmdstr = cmdstr.strip(' &&')
        process = subprocess.Popen(cmdstr,stdout=subprocess.PIPE, shell=True)
        ret = process.communicate()[0]
        if (decode):
            ret = ret.decode('utf-8')
        return ret

    def install_pkgs(self, *paths, editable=False):
        print('Installing Packages: {}'.format(paths))
        commands = []
        for name, p in paths:
            try:
                return __import__(name)
            except ImportError:
                commands += ['pip install {}{}'.format('-e ' if editable else '', p)]
        print(self.subprocess_cmd(*commands))

setup(
    name='noaahistory',
    description='dev package',
    author='rlyon',
    author_email='rlyon14@yahoo.com',
    version='0.1.1',
    packages=['noaahistory',],
    url="https://github.com/rlyon14/noaahistory",
    install_requires=(
        'matplotlib>=3.1.0',
        'numpy',
        'click',
        'pyqt5'
    ),
    entry_points='''
        [console_scripts]
        weather=noaahistory.cli:cli
    ''',
    cmdclass={
        'install': PostInstallCommand,
    }
)