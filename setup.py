from distutils.core import setup

from setuptools.command.test import test as TestCommand
import sys


class PyTest(TestCommand):
    user_options = [('pytest-args=', 'a', "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


setup(
    name='check_project',
    version='0.1.0',
    author='Adam Wolf',
    author_email='adamwolf@feelslikeburning.com',
    packages=['check_project'],
    url='https://github.com/adamwolf/check_project',
    license='GPLv2',
    description='Check project directories for uncommitted or unpushed work and for files like README and LICENSE.',
    long_description=open('README.rst').read(),
    install_requires=[],
    entry_points={
        'console_scripts': ['check_project = check_project.cli:main']
    },
    keywords='unpushed uncommitted style',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: GNU General Public License v2 (GPLv2)',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Environment :: Console',
        'Intended Audience :: Developers',
    ],
    tests_require=['pytest',
                   'pbr>=0.11,<1.7.0',
                   # an issue in September 2015 meant that without this here,
                   # python setup.py test failed while installing pbr
                   'Mock'],
    cmdclass={'test': PyTest},
)
