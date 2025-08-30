#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for input validation and error handling in sample_roads.
"""

import unittest
import tempfile
import os
import csv
from geo_sampling.sample_roads import main


class TestSampleRoadsValidation(unittest.TestCase):
    """Test validation in sample_roads module."""

    def setUp(self):
        """Set up test data."""
        self.test_data = [
            {
                "segment_id": 1,
                "osm_id": "123",
                "osm_name": "Test Road 1",
                "osm_type": "primary",
                "start_lat": 0.0,
                "start_long": 0.0,
                "end_lat": 1.0,
                "end_long": 1.0
            },
            {
                "segment_id": 2,
                "osm_id": "456",
                "osm_name": "Test Road 2",
                "osm_type": "secondary",
                "start_lat": 1.0,
                "start_long": 1.0,
                "end_lat": 2.0,
                "end_long": 2.0
            }
        ]

    def _create_test_csv(self):
        """Create a temporary CSV file with test data."""
        temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        )

        with temp_file as f:
            writer = csv.DictWriter(f, fieldnames=[
                "segment_id", "osm_id", "osm_name", "osm_type",
                "start_lat", "start_long", "end_lat", "end_long"
            ])
            writer.writeheader()
            writer.writerows(self.test_data)

        return temp_file.name

    def test_sample_larger_than_population(self):
        """Test error when sample size exceeds population."""
        test_file = self._create_test_csv()

        try:
            with self.assertRaises(SystemExit) as cm:
                main(['-n', '10', test_file])  # Request more than 2 available
            self.assertEqual(cm.exception.code, -1)
        finally:
            os.unlink(test_file)

    def test_valid_sampling(self):
        """Test valid sampling operation."""
        test_file = self._create_test_csv()
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        output_file.close()

        try:
            # Sample 1 from 2 available
            result = main(['-n', '1', '-o', output_file.name, test_file])
            self.assertEqual(result, 0)

            # Verify output file exists and has content
            self.assertTrue(os.path.exists(output_file.name))

            with open(output_file.name, 'r') as f:
                content = f.read()
                self.assertIn('segment_id', content)  # Header present

        finally:
            os.unlink(test_file)
            os.unlink(output_file.name)

    def test_type_filtering(self):
        """Test filtering by road type."""
        test_file = self._create_test_csv()
        output_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        output_file.close()

        try:
            # Filter for only primary roads
            result = main(['-t', 'primary', '-o', output_file.name, test_file])
            self.assertEqual(result, 0)

            # Verify only primary roads in output
            with open(output_file.name, 'r') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['osm_type'], 'primary')

        finally:
            os.unlink(test_file)
            os.unlink(output_file.name)

    def test_missing_input_file(self):
        """Test error handling for missing input file."""
        with self.assertRaises(FileNotFoundError):
            main(['nonexistent_file.csv'])

    def test_seed_reproducibility(self):
        """Test that using same seed produces same results."""
        test_file = self._create_test_csv()
        output1 = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        output2 = tempfile.NamedTemporaryFile(delete=False, suffix='.csv')
        output1.close()
        output2.close()

        try:
            # Run with same seed twice
            main(['-n', '1', '-s', '42', '-o', output1.name, test_file])
            main(['-n', '1', '-s', '42', '-o', output2.name, test_file])

            # Results should be identical
            with open(output1.name, 'r') as f1, open(output2.name, 'r') as f2:
                self.assertEqual(f1.read(), f2.read())

        finally:
            os.unlink(test_file)
            os.unlink(output1.name)
            os.unlink(output2.name)


if __name__ == '__main__':
    unittest.main()
