#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for sample_roads.py

"""

import os
import unittest

from geo_sampling.sample_roads import main


class TestSampleRoads(unittest.TestCase):
    """Test cases for sample_roads module functionality."""

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_sample(self):
        """Test the sampling functionality."""
        main(['-n', '100', 'output.csv'])
        self.assertTrue(os.path.exists('sample-output.csv'))


if __name__ == '__main__':
    unittest.main()
