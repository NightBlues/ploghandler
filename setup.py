import os
import sys
from setuptools import setup


PACKAGE_PATH = os.path.abspath(os.path.dirname(__file__))

def get_description():
    with open(os.path.join(PACKAGE_PATH, "README.md")) as readme:
        return readme.read()

setup(
    name="ploghandler",
    version="0.2",
    author="Vadim Radovel",
    author_email="vadim@radovel.ru",
    description="Provides concurrent rotating file handler for posix-compatible OSes.",
    license="GPLv3",
    py_modules=["ploghandler"],
    long_description=get_description(),
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
