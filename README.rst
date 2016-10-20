Geo sampling
============

.. image:: https://ci.appveyor.com/api/projects/status/gtm9ao3u7ir4gs0w?svg=true
    :target: https://ci.appveyor.com/project/soodoku/geo_sampling
.. image:: https://travis-ci.org/soodoku/geo_sampling.svg?branch=public
    :target: https://travis-ci.org/soodoku/geo_sampling
.. image:: https://img.shields.io/pypi/v/geo_sampling.svg?maxAge=2592000
    :target: https://pypi.python.org/pypi/geo_sampling
.. image:: https://readthedocs.org/projects/geo-sampling/badge/?version=latest
    :target: http://geo-sampling.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Say you want to learn about the average number of potholes per kilometer of street in a city. Or estimate a similar such quantity. To estimate the quantity, you need to sample locations on the streets. This package helps you sample those locations. In particular, the package implements the following sampling strategy:

1. **Sampling Frame**: Get all the streets in the region of interest from `OpenStreetMap <https://www.openstreetmap.org/#map=5/51.500/-0.100>`_. To accomplish that, the package first downloads administrative boundary data for the country in which the region is located in ESRI format from http://www.gadm.org/country The administrative data is in multiple levels, for instance, cities are nested in states, which are nested in countries. The user can choose a city or state, but not a portion of a city. And then the package uses the `pyshp package <https://pypi.python.org/pypi/pyshp>`_ to build a URL for the site http://extract.bbbike.org from which we can download the OSM data. 

2. **Sampling Design**:
	
	* For each street (or road), starting from one end of the street, we split the street into .5 km segments till we reach the end of the street. (The last segment, or if the street is shorter than .5km, the only segment, can be shorter than .5 km.) 

	* Get the lat/long of starting and ending points of each of the segments. And assume that the street is a straight line between the .5 km segment.  

	* Next, create a database of all the segments 

	* Sample rows from the database and produce a CSV of the sampled segments 

	* Plot the lat/long --- filling all the area within the segment. These shaded regions are regions for which data needs to be collected.

3. **Data Collection**: Collect data on the highlighted segments.

Prerequisites
=============

There are a couple dependencies that need to be built from source on Windows so you may need to install `Microsoft Visual C++ Compiler for Python 2.7 <https://www.microsoft.com/en-us/download/details.aspx?id=44266>`_.

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


Install geo-sampling package from PyPI.

::

    pip install geo-sampling


Documentation
==============

*  `More information on installation <docs/install.rst>`_
*  `Usage <docs/usage.rst>`_
*  `Sample workflow <docs/workflow.rst>`_

For more information please visit the `project documentation page <http://geo-sampling.readthedocs.io/en/latest/>`_.

Authors
=======

Suriyan Laohaprapanon and Gaurav Sood

License
=======

Scripts are released under the `MIT License <LICENSE>`__.