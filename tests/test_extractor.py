#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for RoadExtractor class and road extraction functionality.

This module tests the RoadExtractor class basic functionality without
requiring network operations.
"""

import unittest
from unittest.mock import patch
import tempfile
import os

from geo_sampling.extractor import RoadExtractor, extract_roads
from geo_sampling._types import RoadSegment


class TestRoadExtractor(unittest.TestCase):
    """Test cases for RoadExtractor class."""

    def setUp(self):
        """Set up test data."""
        self.country = "Singapore"
        self.region = "Central"
        self.admin_level = 1
        self.extractor = RoadExtractor(self.country, self.region, self.admin_level)

    def test_extractor_initialization(self):
        """Test RoadExtractor initialization."""
        extractor = RoadExtractor("Thailand", "Bangkok", 2)

        self.assertEqual(extractor.country, "Thailand")
        self.assertEqual(extractor.region, "Bangkok")
        self.assertEqual(extractor.admin_level, 2)

        # Check that data providers are initialized
        self.assertIsNotNone(extractor.gadm)
        self.assertIsNotNone(extractor.osm)

        # Test string representation (basic functionality)
        str_repr = str(extractor)
        self.assertIsInstance(str_repr, str)
        self.assertGreater(len(str_repr), 0)

    def test_road_type_filtering_logic(self):
        """Test road type filtering logic without network calls."""
        # Create test segments
        test_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.1, 103.1, 1.2, 103.2),
            RoadSegment(2, "way_2", "Road 2", "secondary", 1.2, 103.2, 1.3, 103.3),
            RoadSegment(3, "way_3", "Road 3", "tertiary", 1.3, 103.3, 1.4, 103.4),
        ]

        # Test the private filtering method
        # Single type
        filtered = self.extractor._filter_by_road_types(test_segments, ["primary"])
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].osm_type, "primary")

        # Multiple types
        filtered = self.extractor._filter_by_road_types(
            test_segments, ["primary", "secondary"]
        )
        self.assertEqual(len(filtered), 2)

        # No filter (None)
        filtered = self.extractor._filter_by_road_types(test_segments, None)
        self.assertEqual(len(filtered), 3)

        # Empty list filter
        filtered = self.extractor._filter_by_road_types(test_segments, [])
        self.assertEqual(len(filtered), 3)  # Should return all

        # Non-existent type
        filtered = self.extractor._filter_by_road_types(test_segments, ["nonexistent"])
        self.assertEqual(len(filtered), 0)

    def test_caching_behavior(self):
        """Test that extractor properly manages cached data."""
        # Test that cached segments are initially None
        self.assertIsNone(self.extractor._road_segments)

        # Mock some segments
        test_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.1, 103.1, 1.2, 103.2)
        ]

        # Set cached segments
        self.extractor._road_segments = test_segments

        # Test get_available_road_types uses cached data
        available_types = self.extractor.get_available_road_types()
        self.assertEqual(available_types, ["primary"])

    def test_csv_save_functionality(self):
        """Test CSV saving functionality without network operations."""
        # Mock some road segments in the cache
        test_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.1, 103.1, 1.2, 103.2),
            RoadSegment(2, "way_2", "Road 2", "secondary", 1.2, 103.2, 1.3, 103.3),
        ]

        # Set cached data to avoid network calls
        self.extractor._road_segments = test_segments

        # Test CSV saving
        with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
            temp_path = f.name

        try:
            # Mock get_roads to return cached data
            with patch.object(self.extractor, "get_roads", return_value=test_segments):
                self.extractor.save_csv(temp_path)

            # Verify file was created
            self.assertTrue(os.path.exists(temp_path))

            # Verify file has content
            with open(temp_path, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertIn("segment_id", content)  # Header
                self.assertIn("way_1", content)  # Data

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_error_handling_invalid_region(self):
        """Test error handling for invalid region specification."""
        # This test verifies that initialization doesn't fail immediately
        extractor = RoadExtractor("NonexistentCountry", "NonexistentRegion", 1)

        # The actual error should occur during data extraction, not initialization
        self.assertEqual(extractor.country, "NonexistentCountry")
        self.assertEqual(extractor.region, "NonexistentRegion")

    def test_dataframe_conversion(self):
        """Test DataFrame conversion functionality."""
        # Mock some road segments
        test_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.1, 103.1, 1.2, 103.2),
            RoadSegment(2, "way_2", "Road 2", "secondary", 1.2, 103.2, 1.3, 103.3),
        ]

        # Set cached data
        self.extractor._road_segments = test_segments

        try:
            import pandas as pd

            # Mock get_roads to return cached data
            with patch.object(self.extractor, "get_roads", return_value=test_segments):
                df = self.extractor.to_dataframe()

            # Verify DataFrame properties
            self.assertIsInstance(df, pd.DataFrame)
            self.assertEqual(len(df), 2)

            # Check expected columns
            expected_columns = {
                "segment_id",
                "osm_id",
                "osm_name",
                "osm_type",
                "start_lat",
                "start_long",
                "end_lat",
                "end_long",
            }
            self.assertEqual(set(df.columns), expected_columns)

        except ImportError:
            self.skipTest("pandas not available for testing")

    def test_plot_functionality(self):
        """Test plotting functionality without displaying plots."""
        import matplotlib

        matplotlib.use("Agg")  # Non-interactive backend
        import matplotlib.pyplot as plt

        # Mock some road segments
        test_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.1, 103.1, 1.2, 103.2),
        ]

        try:
            # Mock get_roads to return test data
            with patch.object(self.extractor, "get_roads", return_value=test_segments):
                plt.figure()
                self.extractor.plot()
                plt.close()

            # If we get here, plotting worked without errors
            self.assertTrue(True, "Plotting functionality works")

        except Exception as e:
            self.fail(f"Plotting functionality failed: {e}")


class TestExtractRoadsUtilityFunction(unittest.TestCase):
    """Test the utility extract_roads function."""

    def test_extract_roads_function_exists(self):
        """Test that the extract_roads function exists and can be imported."""
        # This is a basic test to ensure the function is properly exposed

        # Check that it's callable
        self.assertTrue(callable(extract_roads))

        # Check basic signature (without calling it to avoid network operations)
        import inspect

        sig = inspect.signature(extract_roads)

        # Verify expected parameters exist
        expected_params = {
            "country",
            "region",
            "admin_level",
            "road_types",
            "segment_length",
            "data_dir",
        }
        actual_params = set(sig.parameters.keys())
        self.assertEqual(actual_params, expected_params)

        # Verify some defaults
        self.assertEqual(sig.parameters["admin_level"].default, 1)
        self.assertEqual(sig.parameters["segment_length"].default, 500)
        self.assertEqual(sig.parameters["data_dir"].default, "data")


class TestExtractorDataValidation(unittest.TestCase):
    """Test data validation in the extractor."""

    def setUp(self):
        """Set up test extractor."""
        self.extractor = RoadExtractor("Test", "Test", 1)

    def test_road_segment_validation(self):
        """Test that extracted road segments are properly validated."""
        # Create test segments with various data quality issues
        test_segments = [
            # Valid segment
            RoadSegment(1, "way_1", "Good Road", "primary", 1.1, 103.1, 1.2, 103.2),
            # Segment with empty name
            RoadSegment(2, "way_2", "", "secondary", 1.2, 103.2, 1.3, 103.3),
            # Segment with same start and end (zero length)
            RoadSegment(3, "way_3", "Point Road", "tertiary", 1.3, 103.3, 1.3, 103.3),
        ]

        # Set cached segments
        self.extractor._road_segments = test_segments

        # Test filtering works with various data quality issues
        filtered = self.extractor._filter_by_road_types(test_segments, ["primary"])
        self.assertEqual(len(filtered), 1)
        self.assertIsInstance(filtered[0], RoadSegment)

    def test_coordinate_validation(self):
        """Test validation of coordinate ranges."""
        # Test segments with extreme coordinates
        test_segments = [
            # Valid coordinates
            RoadSegment(1, "way_1", "Normal", "primary", 1.0, 103.0, 2.0, 104.0),
            # Extreme coordinates (but technically valid)
            RoadSegment(2, "way_2", "Extreme", "secondary", -90.0, -180.0, 90.0, 180.0),
        ]

        # Test filtering accepts all coordinates
        filtered = self.extractor._filter_by_road_types(test_segments, None)
        self.assertEqual(len(filtered), 2)

        # Check that all returned items are RoadSegment objects
        for road in filtered:
            self.assertIsInstance(road, RoadSegment)
            # Verify coordinates are numbers
            self.assertIsInstance(road.start_lat, (int, float))
            self.assertIsInstance(road.start_long, (int, float))
            self.assertIsInstance(road.end_lat, (int, float))
            self.assertIsInstance(road.end_long, (int, float))


if __name__ == "__main__":
    unittest.main(verbosity=2)
