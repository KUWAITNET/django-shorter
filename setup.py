import os
from setuptools import setup, find_packages
import tinylinks


def read(fname):
    try:
        return open(os.path.join(os.path.dirname(__file__), fname)).read()
    except IOError:
        return ""


setup(
    name="django-tinylinks",
    version=tinylinks.__version__,
    description=read("DESCRIPTION"),
    long_description=read("README.rst"),
    license="The MIT License",
    platforms=["OS Independent"],
    keywords="django, url shortener, link shortener",
    author="Tobias Lorenz",
    author_email="tobias.lorenz@bitmazk.com",
    url="https://github.com/bitmazk/django-tinylinks",
    packages=find_packages(),
    include_package_data=True,
    tests_require=[
        "factory_boy",
    ],
    test_suite="tinylinks.tests.runtests.runtests",
)
