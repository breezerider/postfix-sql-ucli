========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|

    * - build
      - |github-actions| |codecov|

..     * - package
..       - | |license| |version| |wheel| |supported-versions|
..         | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/postfix-sql-ucli/badge/?style=flat
    :target: https://postfix-sql-ucli.readthedocs.io/
    :alt: Documentation Status

.. |github-actions| image:: https://github.com/breezerider/postfix-sql-ucli/actions/workflows/github-actions.yml/badge.svg
    :alt: GitHub Actions Build Status
    :target: https://github.com/breezerider/postfix-sql-ucli/actions

.. |codecov| image:: https://codecov.io/gh/breezerider/postfix-sql-ucli/branch/main/graphs/badge.svg?branch=main
    :alt: Coverage Status
    :target: https://app.codecov.io/github/breezerider/postfix-sql-ucli

.. .. |license| image:: https://img.shields.io/badge/license-BSD-green?style=flat
..     :alt: PyPI Package license
..     :target: https://test.pypi.org/project/postfix-sql-ucli
..
.. .. |version| image:: https://img.shields.io/badge/test.pypi-v0.0.0-informational?style=flat
..     :alt: PyPI Package latest release
..     :target: https://test.pypi.org/project/postfix-sql-ucli
..
.. .. |wheel| image:: https://img.shields.io/badge/wheel-yes-success?style=flat
..     :alt: PyPI Wheel
..     :target: https://test.pypi.org/project/postfix-sql-ucli
..
.. .. |supported-versions| image:: https://img.shields.io/badge/python-3.8_|_3.9_|_3.10_|_3.11-informational?style=flat
..     :alt: Supported Python versions
..     :target: https://test.pypi.org/project/postfix-sql-ucli

.. .. |commits-since| image:: https://img.shields.io/github/commits-since/breezerider/postfix-sql-ucli/v0.0.0.svg
..     :alt: Commits since latest release
..     :target: https://github.com/breezerider/postfix-sql-ucli/compare/v0.0.0...main

.. end-badges

Minimal CLI administration tool for managing Postfix virtual maps stored in a SQL database.
Tool supports basic operations on following entities:

* domains: add / search
* user: add / search / delete
* alias: add / search / delete

and verifies input arguments to these operations.
It depends on other common packages:

* click
* passlib
* sqlalchemy
* pyyaml

Installation
============

Get latest released version from `PyPI <https://pypi.org/>`_::

    pip install postfix-sql-ucli

You can also install the in-development version with::

    pip install https://github.com/breezerider/postfix-sql-ucli/archive/main.zip


Documentation
=============


https://postfix-sql-ucli.readthedocs.io/


License
=======

- Source code: `BSD-3-Clause <https://choosealicense.com/licenses/bsd-3-clause/>`_ license unless noted otherwise in individual files/directories
- Documentation: `Creative Commons Attribution-ShareAlike 4.0 <https://creativecommons.org/licenses/by-sa/4.0/>`_ license


Development
===========

To run all the tests issue this command in a terminal::

    tox
