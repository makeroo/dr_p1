#!/usr/bin/env python

import sys
import os
from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
from distutils.core import Command


PACKAGE_NAME = "dr_p1"
PACKAGE_ROOT = "dr"
PACKAGE_URL = "https://github.com/makeroo/dr_p1"
VERSION = "0.0.1"
DESCRIPTION = "First prototype of DR project"
AUTHOR_NAME = "Simone Pierazzini"
AUTHOR_EMAIL = "makeroo@gmail.com"
SCRIPTS = [
]
TEST_SUITE = "tests"
INSTALL_REQUIRES = open("requirements.txt").readlines()
CLASSIFIERS = [
    "Development Status :: 1 - Planning",
    "Intended Audience :: Developers",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Programming Language :: Python :: 3",
    "Programming Language :: Python :: Implementation :: CPython",
    # "Programming Language :: Python :: Implementation :: PyPy",
    # "Programming Language :: Python :: Implementation :: Jython",
]

# try:
#    from ez_setup import use_setuptools
#    use_setuptools()
# except ImportError:
#    pass


class CleanCommand(Command):
    description = "Clean leftovers of previous builds, tox and test runs"
    user_options = []

    def initialize_options(self):
        self.cwd = None

    def finalize_options(self):
        self.cwd = os.getcwd()

    def run(self):
        assert os.getcwd() == self.cwd, 'Must be in package root: %s' % self.cwd
        os.system("rm -fr "
                  ".eggs "
                  ".tox "
                  "build "
                  "dist "
                  ".coverage coverage-report "
                  "*.egg-info setuptools-*.egg setuptools-*.zip")
        os.system('find . -name __pycache__ '
                  '-o -name \\*.pyc '
                  '-o -name \\*.pyo '
                  '| xargs rm -fr ')


class TestCoverageCommand(Command):
    description = "Run the test suite, producing code coverage report"
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        os.system("coverage run --branch --source=%s setup.py test" % PACKAGE_ROOT)
        os.system("coverage html --directory=coverage-report")
        indexfile = os.path.join("coverage-report", "index.html")
        if os.path.isfile(indexfile):
            local_url = "file:///" + os.path.abspath(indexfile).replace("\\", "/")
            import webbrowser
            webbrowser.open(local_url)

setup_requires = []
tests_require = []
other_commands = {
    "clean": CleanCommand,
    "coverage": TestCoverageCommand,
}

if "coverage" in sys.argv:
    tests_require += [
        "coverage",
    ]

if "test" in sys.argv:
    setup_requires.append('pytest-runner')
    tests_require.append('pytest')


def namespace_packages():
    """any package higher than PACKAGE_ROOT is certainly a namespace package.

    Namespace packages can be common to several different Python egg installed
    artifacts. setup() wants to know their name to respect that during the install
    phase.

    This function deduces their name"""
    result = []
    toks = PACKAGE_ROOT.split(".")
    for i in range(1, len(toks)):
        result.append(".".join(toks[:i]))
    return result


setup(
    name=PACKAGE_NAME,
    version=VERSION,
    description=DESCRIPTION,
    author=AUTHOR_NAME,
    author_email=AUTHOR_EMAIL,
    url=PACKAGE_URL,
    zip_safe=False,  # unnecessary; it avoids egg-as-zipfile install
    # gentoo setuptools fails to build if namespaces packages does not contain __init__.py...
    packages=find_packages(exclude=['tests']),  # + namespace_packages()),
    namespace_packages=namespace_packages(),
    setup_requires=setup_requires,
    install_requires=INSTALL_REQUIRES,
    scripts=SCRIPTS,
    tests_require=tests_require,
    cmdclass=other_commands,
    classifiers=CLASSIFIERS,
    test_suite=TEST_SUITE,
)
