import os
import sys
from setuptools import setup


PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))

def get_description():
    with open(os.path.join(PACKAGE_PATH, "README.rst")) as readme:
        return readme.read()

setup(
    name="ploghandler",
    version="0.4.1",
    author="Vadim Radovel",
    author_email="vadim@radovel.ru",
    description="Provides concurrent rotating file handler for posix-compatible OSes.",
    license="GPLv3",
    url="https://github.com/NightBlues/ploghandler",
    py_modules=["ploghandler"],
    test_suite="test",
    long_description=get_description(),
    platforms = ["posix"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: System :: Logging"
    ]
)
