#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for geo_roads.py

"""

import os
import shutil
import unittest
from geo_sampling.geo_roads import main
from . import capture

COUNTRY_NAME = os.environ.get('COUNTRY_NAME', 'Singapore')
REGION_NAME = os.environ.get('REGION_NAME', 'North')
ADM_LEVEL = os.environ.get('ADM_LEVEL', '1')


@unittest.skipIf(COUNTRY_NAME is None, 'No COUNTRY_NAME found in environment.')
class TestGeoRoads(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        shutil.rmtree('data')

    def test_geo_roads(self):
        with capture(main, ['-l', ADM_LEVEL, '-c', COUNTRY_NAME, '-n',
                            REGION_NAME]) as output:
            self.assertRegex(output, r'Done$')


if __name__ == '__main__':
    unittest.main()
