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
from .test_utils import TestDataMixin


class TestSampleRoadsValidation(TestDataMixin, unittest.TestCase):
    """Test validation in sample_roads module."""

    def test_sample_larger_than_population(self):
        """Test error when sample size exceeds population."""
        test_file = self.create_test_csv()

        try:
            with self.assertRaises(SystemExit) as context_manager:
                main(['-n', '10', test_file])  # Request more than 2 available
            self.assertEqual(context_manager.exception.code, -1)
        finally:
            self.cleanup_temp_file(test_file)

    def test_valid_sampling(self):
        """Test valid sampling operation."""
        test_file = self.create_test_csv()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_output:
            output_file_name = temp_output.name

        try:
            # Sample 1 from 2 available
            result = main(['-n', '1', '-o', output_file_name, test_file])
            self.assertEqual(result, 0)

            # Verify output file exists and has content
            self.assertTrue(os.path.exists(output_file_name))

            with open(output_file_name, 'r', encoding='utf-8') as csv_file:
                content = csv_file.read()
                self.assertIn('segment_id', content)  # Header present

        finally:
            self.cleanup_temp_file(test_file)
            self.cleanup_temp_file(output_file_name)

    def test_type_filtering(self):
        """Test filtering by road type."""
        test_file = self.create_test_csv()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_output:
            output_file_name = temp_output.name

        try:
            # Filter for only primary roads
            result = main(['-t', 'primary', '-o', output_file_name, test_file])
            self.assertEqual(result, 0)

            # Verify only primary roads in output
            with open(output_file_name, 'r', encoding='utf-8') as csv_file:
                reader = csv.DictReader(csv_file)
                rows = list(reader)
                self.assertEqual(len(rows), 1)
                self.assertEqual(rows[0]['osm_type'], 'primary')

        finally:
            self.cleanup_temp_file(test_file)
            self.cleanup_temp_file(output_file_name)

    def test_missing_input_file(self):
        """Test error handling for missing input file."""
        with self.assertRaises(FileNotFoundError):
            main(['nonexistent_file.csv'])

    def test_seed_reproducibility(self):
        """Test that using same seed produces same results."""
        test_file = self.create_test_csv()
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as output1:
            output1_name = output1.name
        with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as output2:
            output2_name = output2.name

        try:
            # Run with same seed twice
            main(['-n', '1', '-s', '42', '-o', output1_name, test_file])
            main(['-n', '1', '-s', '42', '-o', output2_name, test_file])

            # Results should be identical
            with open(output1_name, 'r', encoding='utf-8') as file1, \
                 open(output2_name, 'r', encoding='utf-8') as file2:
                self.assertEqual(file1.read(), file2.read())

        finally:
            self.cleanup_temp_file(test_file)
            self.cleanup_temp_file(output1_name)
            self.cleanup_temp_file(output2_name)


if __name__ == '__main__':
    unittest.main()
