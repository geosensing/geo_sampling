Installation
############

Prerequisites
=============

There are a couple dependencies that need to be built from the source on Windows so you may need to install `Microsoft Visual C++ Compiler for Python 2.7 <https://www.microsoft.com/en-us/download/details.aspx?id=44266>`_.

Installation
============

Prepare the working directory. We recommend that you install in the Python virtual environment.

::

    mkdir geo_sampling
    cd geo_sampling
    virtualenv -p python2.7 venv
    . venv/bin/activate

Upgrade Python packages `pip` and `setuptools` to the latest version.

::

    pip install --upgrade pip setuptools


Install geo-sampling package from test PyPI.

::

    pip install --extra-index-url https://testpypi.python.org/pypi geo-sampling
