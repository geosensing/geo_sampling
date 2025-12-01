#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for geo_sampling type definitions and data structures.

This module tests the RoadSegment and BoundingBox dataclasses to ensure
proper serialization, validation, and type safety.
"""

import unittest

from geo_sampling._types import RoadSegment, BoundingBox, RoadTypeFilter


class TestRoadSegment(unittest.TestCase):
    """Test cases for RoadSegment dataclass."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = {
            "segment_id": 123,
            "osm_id": "way_456789",
            "osm_name": "Main Street",
            "osm_type": "primary",
            "start_lat": 1.3521,
            "start_long": 103.8198,
            "end_lat": 1.3531,
            "end_long": 103.8208,
        }

        self.sample_segment = RoadSegment(
            segment_id=123,
            osm_id="way_456789",
            osm_name="Main Street",
            osm_type="primary",
            start_lat=1.3521,
            start_long=103.8198,
            end_lat=1.3531,
            end_long=103.8208,
        )

    def test_segment_creation(self):
        """Test RoadSegment can be created with all required fields."""
        segment = RoadSegment(
            segment_id=1,
            osm_id="test_id",
            osm_name="Test Road",
            osm_type="secondary",
            start_lat=0.0,
            start_long=0.0,
            end_lat=1.0,
            end_long=1.0,
        )

        self.assertEqual(segment.segment_id, 1)
        self.assertEqual(segment.osm_id, "test_id")
        self.assertEqual(segment.osm_name, "Test Road")
        self.assertEqual(segment.osm_type, "secondary")
        self.assertEqual(segment.start_lat, 0.0)
        self.assertEqual(segment.start_long, 0.0)
        self.assertEqual(segment.end_lat, 1.0)
        self.assertEqual(segment.end_long, 1.0)

    def test_from_dict(self):
        """Test creating RoadSegment from dictionary (CSV row format)."""
        segment = RoadSegment.from_dict(self.sample_data)

        self.assertEqual(segment.segment_id, 123)
        self.assertEqual(segment.osm_id, "way_456789")
        self.assertEqual(segment.osm_name, "Main Street")
        self.assertEqual(segment.osm_type, "primary")
        self.assertAlmostEqual(segment.start_lat, 1.3521, places=6)
        self.assertAlmostEqual(segment.start_long, 103.8198, places=6)
        self.assertAlmostEqual(segment.end_lat, 1.3531, places=6)
        self.assertAlmostEqual(segment.end_long, 103.8208, places=6)

    def test_to_dict(self):
        """Test converting RoadSegment to dictionary (CSV output format)."""
        result = self.sample_segment.to_dict()

        self.assertEqual(result, self.sample_data)
        self.assertIsInstance(result, dict)

        # Check all expected keys are present
        expected_keys = {
            "segment_id",
            "osm_id",
            "osm_name",
            "osm_type",
            "start_lat",
            "start_long",
            "end_lat",
            "end_long",
        }
        self.assertEqual(set(result.keys()), expected_keys)

    def test_roundtrip_conversion(self):
        """Test that dict -> RoadSegment -> dict preserves data."""
        # Start with dict
        segment = RoadSegment.from_dict(self.sample_data)
        result_dict = segment.to_dict()

        self.assertEqual(result_dict, self.sample_data)

        # Start with RoadSegment
        dict_data = self.sample_segment.to_dict()
        recreated_segment = RoadSegment.from_dict(dict_data)

        self.assertEqual(recreated_segment, self.sample_segment)

    def test_type_conversion(self):
        """Test proper type conversion in from_dict."""
        # Test with string numeric values (as from CSV)
        string_data = {
            "segment_id": "123",
            "osm_id": "way_456789",
            "osm_name": "Main Street",
            "osm_type": "primary",
            "start_lat": "1.3521",
            "start_long": "103.8198",
            "end_lat": "1.3531",
            "end_long": "103.8208",
        }

        segment = RoadSegment.from_dict(string_data)

        # Check types are properly converted
        self.assertIsInstance(segment.segment_id, int)
        self.assertIsInstance(segment.osm_id, str)
        self.assertIsInstance(segment.osm_name, str)
        self.assertIsInstance(segment.osm_type, str)
        self.assertIsInstance(segment.start_lat, float)
        self.assertIsInstance(segment.start_long, float)
        self.assertIsInstance(segment.end_lat, float)
        self.assertIsInstance(segment.end_long, float)

        # Check values are correct
        self.assertEqual(segment.segment_id, 123)
        self.assertAlmostEqual(segment.start_lat, 1.3521, places=6)

    def test_equality(self):
        """Test RoadSegment equality comparison."""
        segment1 = RoadSegment(1, "id1", "name", "type", 0.0, 0.0, 1.0, 1.0)
        segment2 = RoadSegment(1, "id1", "name", "type", 0.0, 0.0, 1.0, 1.0)
        segment3 = RoadSegment(2, "id1", "name", "type", 0.0, 0.0, 1.0, 1.0)

        self.assertEqual(segment1, segment2)
        self.assertNotEqual(segment1, segment3)

    def test_str_representation(self):
        """Test string representation of RoadSegment."""
        segment = RoadSegment(1, "way_123", "Test Road", "primary", 0.0, 0.0, 1.0, 1.0)
        str_repr = str(segment)

        # Should contain key information
        self.assertIn("RoadSegment", str_repr)
        self.assertIn("way_123", str_repr)
        self.assertIn("Test Road", str_repr)
        self.assertIn("primary", str_repr)

    def test_invalid_data_handling(self):
        """Test handling of invalid or missing data."""
        # Missing required field should raise error
        incomplete_data = {
            "segment_id": "123",
            "osm_id": "way_456789",
            # Missing other required fields
        }

        with self.assertRaises(KeyError):
            RoadSegment.from_dict(incomplete_data)

        # Invalid numeric conversion should raise error
        invalid_data = {
            "segment_id": "not_a_number",
            "osm_id": "way_456789",
            "osm_name": "Main Street",
            "osm_type": "primary",
            "start_lat": "1.3521",
            "start_long": "103.8198",
            "end_lat": "1.3531",
            "end_long": "103.8208",
        }

        with self.assertRaises(ValueError):
            RoadSegment.from_dict(invalid_data)


class TestBoundingBox(unittest.TestCase):
    """Test cases for BoundingBox dataclass."""

    def test_bounding_box_creation(self):
        """Test BoundingBox can be created with coordinate values."""
        bbox = BoundingBox(min_lat=1.0, max_lat=2.0, min_long=103.0, max_long=104.0)

        self.assertEqual(bbox.min_lat, 1.0)
        self.assertEqual(bbox.max_lat, 2.0)
        self.assertEqual(bbox.min_long, 103.0)
        self.assertEqual(bbox.max_long, 104.0)

    def test_bounding_box_equality(self):
        """Test BoundingBox equality comparison."""
        bbox1 = BoundingBox(1.0, 2.0, 103.0, 104.0)
        bbox2 = BoundingBox(1.0, 2.0, 103.0, 104.0)
        bbox3 = BoundingBox(1.1, 2.0, 103.0, 104.0)

        self.assertEqual(bbox1, bbox2)
        self.assertNotEqual(bbox1, bbox3)

    def test_bounding_box_validation(self):
        """Test logical validation of bounding box coordinates."""
        # Valid bounding box
        bbox = BoundingBox(1.0, 2.0, 103.0, 104.0)

        # Check that min values are less than max values
        self.assertLess(bbox.min_lat, bbox.max_lat)
        self.assertLess(bbox.min_long, bbox.max_long)

    def test_str_representation(self):
        """Test string representation of BoundingBox."""
        bbox = BoundingBox(1.0, 2.0, 103.0, 104.0)
        str_repr = str(bbox)

        self.assertIn("BoundingBox", str_repr)
        self.assertIn("1.0", str_repr)
        self.assertIn("2.0", str_repr)
        self.assertIn("103.0", str_repr)
        self.assertIn("104.0", str_repr)


class TestRoadTypeFilter(unittest.TestCase):
    """Test cases for RoadTypeFilter type alias."""

    def test_road_type_filter_types(self):
        """Test that RoadTypeFilter accepts expected types."""
        # Should accept None
        filter_none: RoadTypeFilter = None
        self.assertIsNone(filter_none)

        # Should accept single string
        filter_string: RoadTypeFilter = "primary"
        self.assertEqual(filter_string, "primary")

        # Should accept list of strings
        filter_list: RoadTypeFilter = ["primary", "secondary"]
        self.assertEqual(filter_list, ["primary", "secondary"])

    def test_road_type_filter_usage(self):
        """Test typical usage patterns for RoadTypeFilter."""

        def process_road_types(road_types: RoadTypeFilter) -> list:
            """Example function that processes road type filter."""
            if road_types is None:
                return []
            elif isinstance(road_types, str):
                return [road_types]
            else:
                return list(road_types)

        # Test with None
        self.assertEqual(process_road_types(None), [])

        # Test with single string
        self.assertEqual(process_road_types("primary"), ["primary"])

        # Test with list
        self.assertEqual(
            process_road_types(["primary", "secondary"]), ["primary", "secondary"]
        )


class TestDataIntegrity(unittest.TestCase):
    """Test data integrity and consistency across type operations."""

    def test_coordinate_precision(self):
        """Test that coordinate precision is maintained."""
        # High precision coordinates
        precise_data = {
            "segment_id": 1,
            "osm_id": "way_123",
            "osm_name": "Test",
            "osm_type": "primary",
            "start_lat": 1.12345678901234,
            "start_long": 103.87654321098765,
            "end_lat": 1.12345678901235,
            "end_long": 103.87654321098766,
        }

        segment = RoadSegment.from_dict(precise_data)
        result = segment.to_dict()

        # Check that precision is reasonably maintained
        self.assertAlmostEqual(
            result["start_lat"], precise_data["start_lat"], places=10
        )
        self.assertAlmostEqual(
            result["start_long"], precise_data["start_long"], places=10
        )

    def test_unicode_handling(self):
        """Test handling of Unicode characters in road names."""
        unicode_data = {
            "segment_id": 1,
            "osm_id": "way_123",
            "osm_name": "Jalan Besar 大路",  # Mixed English and Chinese
            "osm_type": "primary",
            "start_lat": 1.0,
            "start_long": 103.0,
            "end_lat": 1.1,
            "end_long": 103.1,
        }

        segment = RoadSegment.from_dict(unicode_data)
        result = segment.to_dict()

        self.assertEqual(result["osm_name"], "Jalan Besar 大路")
        self.assertEqual(segment.osm_name, "Jalan Besar 大路")

    def test_edge_case_coordinates(self):
        """Test edge cases for coordinate values."""
        # Zero coordinates
        zero_data = {
            "segment_id": 1,
            "osm_id": "way_123",
            "osm_name": "Test",
            "osm_type": "primary",
            "start_lat": 0.0,
            "start_long": 0.0,
            "end_lat": 0.0,
            "end_long": 0.0,
        }

        segment = RoadSegment.from_dict(zero_data)
        self.assertEqual(segment.start_lat, 0.0)
        self.assertEqual(segment.start_long, 0.0)

        # Negative coordinates
        negative_data = zero_data.copy()
        negative_data.update(
            {
                "start_lat": -1.0,
                "start_long": -103.0,
                "end_lat": -1.1,
                "end_long": -103.1,
            }
        )

        segment = RoadSegment.from_dict(negative_data)
        self.assertEqual(segment.start_lat, -1.0)
        self.assertEqual(segment.start_long, -103.0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
