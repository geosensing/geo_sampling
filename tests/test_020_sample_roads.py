#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for sample_roads.py

"""

import os
import unittest

from geo_sampling.sample_roads import main


class TestSampleRoads(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sample(self):
        main(['-n', '100', 'output.csv'])
        self.assertTrue(os.path.exists('sample-output.csv'))


if __name__ == '__main__':
    unittest.main()
