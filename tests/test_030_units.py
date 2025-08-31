#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Unit tests for individual functions in geo_sampling.
"""

import csv
import os
import tempfile
import unittest
from io import StringIO
from unittest.mock import patch

from shapely.geometry import LineString
from shapely.geometry import Point

from geo_sampling.geo_roads import (
    redistribute_vertices,
    output_to_file,
    _setup_data_directory
)
from geo_sampling.utils import write_csv
from .test_utils import TestDataMixin


class TestRedistributeVertices(unittest.TestCase):
    """Test the redistribute_vertices function."""

    def test_linestring_redistribution(self):
        """Test redistribution of vertices in a LineString."""
        # Create a simple line from (0,0) to (100,0)
        line = LineString([(0, 0), (100, 0)])

        # Redistribute vertices every 25 meters
        result = redistribute_vertices(line, 25)

        # Should have 5 segments (4 divisions + endpoint)
        self.assertEqual(len(result.coords), 5)

        # Check first and last points are preserved
        self.assertEqual(result.coords[0], (0, 0))
        self.assertEqual(result.coords[-1], (100, 0))

    def test_short_linestring(self):
        """Test redistribution with line shorter than distance."""
        line = LineString([(0, 0), (10, 0)])
        result = redistribute_vertices(line, 25)

        # Should have at least start and end points
        self.assertGreaterEqual(len(result.coords), 2)

    def test_invalid_geometry(self):
        """Test handling of invalid geometry types."""
        point = Point(0, 0)

        with self.assertRaises(ValueError):
            redistribute_vertices(point, 25)


class TestOutputToFile(unittest.TestCase):
    """Test the output_to_file function."""

    def test_output_segments(self):
        """Test writing segments to CSV."""
        # Create mock writer
        output = StringIO()
        writer = csv.DictWriter(output, fieldnames=[
            "segment_id", "osm_id", "osm_name", "osm_type",
            "start_lat", "start_long", "end_lat", "end_long"
        ])

        # Create test line
        line = LineString([(0, 0), (1, 1), (2, 2)])

        # Write segments
        uid = output_to_file(writer, 0, "123", "Test Road", "primary", line)

        # Check that segments were written
        self.assertEqual(uid, 2)  # Two segments written


class TestUtils(TestDataMixin, unittest.TestCase):
    """Test utility functions."""

    def test_write_csv(self):
        """Test CSV writing functionality."""
        test_data = [self.sample_test_data[0]]  # Use first item from shared data

        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        ) as temp_csv:
            temp_path = temp_csv.name

        try:
            write_csv(temp_path, test_data)

            # Verify file was created and contains data
            self.assertTrue(os.path.exists(temp_path))

            with open(temp_path, 'r', encoding='utf-8') as csv_file:
                content = csv_file.read()
                self.assertIn("segment_id", content)
                self.assertIn("Test Road 1", content)

        finally:
            self.cleanup_temp_file(temp_path)

    def test_write_csv_no_header(self):
        """Test CSV writing without header."""
        test_data = [{"segment_id": 1, "osm_id": "123"}]

        with tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        ) as temp_csv:
            temp_path = temp_csv.name

        try:
            write_csv(temp_path, test_data, no_header=True)

            with open(temp_path, 'r', encoding='utf-8') as csv_file:
                content = csv_file.read()
                self.assertNotIn("segment_id", content)  # No header

        finally:
            self.cleanup_temp_file(temp_path)


class TestHelperFunctions(unittest.TestCase):
    """Test helper functions."""

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_setup_data_directory(self, mock_makedirs, mock_exists):
        """Test data directory setup."""
        mock_exists.return_value = False

        _setup_data_directory()

        mock_exists.assert_called_once_with("data")
        mock_makedirs.assert_called_once_with("data")

    @patch('os.path.exists')
    @patch('os.makedirs')
    def test_setup_data_directory_exists(self, mock_makedirs, mock_exists):
        """Test data directory setup when directory exists."""
        mock_exists.return_value = True

        _setup_data_directory()

        mock_exists.assert_called_once_with("data")
        mock_makedirs.assert_not_called()


if __name__ == '__main__':
    unittest.main()
