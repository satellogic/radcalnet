=========
radcalnet
=========

|Build Status|_ |Coverage Status|

Python package for easy access to the measurements published by RadCalNet_.

RadCalNet is a CEOS_ initiative, providing relevant measurements and estimated reflectance
factors, based on data from multiple calibration sites around the world.
The data is provided in a textual format with published specs_. Available as a `full archive`_
(zip file), or as smaller daily downloads.

This package provides functions for parsing these files and extracting measurements as
Pandas DataFrame_ objects ready for analysis.

.. _RadCalNet: https://www.radcalnet.org

.. _CEOS: http://ceos.org/

.. _specs: https://www.radcalnet.org/documentation/RadCalNetGenDoc/R2-RadCalNetRequirements-DataFormatSpecification_V8.pdf

.. _full archive: https://www.radcalnet.org/allData

.. _DataFrame: https://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html

.. |Build Status| image:: https://travis-ci.org/satellogic/radcalnet.svg?branch=master
	          :alt: Build Status
.. _Build Status: https://travis-ci.org/satellogic/radcalnet

.. |Coverage Status| image:: https://satellogic.github.io/radcalnet/coverage.svg
                     :alt: Coverage Status

Usage:

.. image:: https://user-images.githubusercontent.com/17533233/43774947-9278c6e2-9a53-11e8-8b74-684904b8a4b7.png
