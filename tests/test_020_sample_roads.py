#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for sample_roads.py

"""

import os
import unittest
import csv

from geo_sampling.sample_roads import main


class TestSampleRoads(unittest.TestCase):
    """Test cases for sample_roads module functionality."""

    def setUp(self):
        """Create test input CSV file."""
        self.test_csv = "test_input.csv"
        # Create test data with road segments using expected field names
        with open(self.test_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(
                [
                    "segment_id",
                    "osm_id",
                    "osm_name",
                    "osm_type",
                    "start_lat",
                    "start_long",
                    "end_lat",
                    "end_long",
                ]
            )
            for i in range(200):  # Create 200 test road segments
                writer.writerow(
                    [
                        i,
                        f"osm_{i}",
                        f"Road {i}",
                        f"type_{i % 5}",
                        1.3 + i * 0.001,
                        103.8 + i * 0.001,
                        1.3 + (i + 1) * 0.001,
                        103.8 + (i + 1) * 0.001,
                    ]
                )

    def tearDown(self):
        """Clean up test files."""
        for f in [self.test_csv, "sample-output.csv"]:
            if os.path.exists(f):
                os.remove(f)

    def test_sample(self):
        """Test the sampling functionality."""
        main(["-n", "100", self.test_csv])
        self.assertTrue(os.path.exists("sample-output.csv"))


if __name__ == "__main__":
    unittest.main()
