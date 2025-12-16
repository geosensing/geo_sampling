#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Tests for RoadSampler class and sampling functionality.

This module tests the core sampling logic including random sampling,
stratified sampling, and various filtering operations.
"""

import os
import tempfile
import unittest
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

from geo_sampling.sampler import RoadSampler, load_segments_from_csv, sample_roads
from geo_sampling._types import RoadSegment


class TestRoadSampler(unittest.TestCase):
    """Test cases for RoadSampler class."""

    def setUp(self):
        """Set up test data."""
        # Create diverse test segments with multiple road types
        self.test_segments = []
        road_types = ["primary", "secondary", "tertiary", "residential", "trunk"]

        for i in range(50):
            road_type = road_types[i % len(road_types)]
            self.test_segments.append(
                RoadSegment(
                    segment_id=i + 1,
                    osm_id=f"way_{i}",
                    osm_name=f"Test Road {i}",
                    osm_type=road_type,
                    start_lat=1.3 + i * 0.001,
                    start_long=103.8 + i * 0.001,
                    end_lat=1.3 + (i + 1) * 0.001,
                    end_long=103.8 + (i + 1) * 0.001,
                )
            )

        self.sampler = RoadSampler(self.test_segments)

    def test_sampler_initialization(self):
        """Test RoadSampler initialization and validation."""
        # Valid initialization
        sampler = RoadSampler(self.test_segments)
        self.assertEqual(len(sampler.segments), 50)

        # Empty segments should raise error
        with self.assertRaises(ValueError):
            RoadSampler([])

        # Non-RoadSegment objects should raise error
        with self.assertRaises(ValueError):
            RoadSampler(["not", "road", "segments"])

    def test_random_sampling(self):
        """Test random sampling functionality."""
        # Basic random sampling
        sample = self.sampler.random_sample(10)
        self.assertEqual(len(sample), 10)
        self.assertTrue(all(isinstance(s, RoadSegment) for s in sample))

        # Test with seed for reproducibility
        sample1 = self.sampler.random_sample(5, seed=42)
        sample2 = self.sampler.random_sample(5, seed=42)
        self.assertEqual(sample1, sample2)  # Should be identical

        # Different seeds should give different results (usually)
        sample3 = self.sampler.random_sample(5, seed=123)
        self.assertNotEqual(sample1, sample3)  # Very likely to be different

    def test_random_sampling_edge_cases(self):
        """Test edge cases for random sampling."""
        # Sample size equals population size
        sample = self.sampler.random_sample(50)
        self.assertEqual(len(sample), 50)
        # Check all segments are included (order may differ)
        sample_ids = [s.segment_id for s in sample]
        original_ids = [s.segment_id for s in self.test_segments]
        self.assertEqual(sorted(sample_ids), sorted(original_ids))

        # Sample size larger than population should raise error
        with self.assertRaises(ValueError):
            self.sampler.random_sample(100)

        # Zero sample size should return empty list
        sample = self.sampler.random_sample(0)
        self.assertEqual(len(sample), 0)
        self.assertIsInstance(sample, list)

        # Negative sample size should return empty list
        sample = self.sampler.random_sample(-5)
        self.assertEqual(len(sample), 0)

    def test_stratified_sampling(self):
        """Test stratified sampling functionality."""
        # Basic stratified sampling
        sample = self.sampler.stratified_sample(20, seed=42)
        self.assertEqual(len(sample), 20)

        # Check that all road types are represented
        sample_types = set(s.osm_type for s in sample)
        original_types = set(s.osm_type for s in self.test_segments)
        self.assertTrue(
            len(sample_types) > 1, "Stratified sample should include multiple types"
        )

        # Test proportional representation
        original_counts = {}
        for segment in self.test_segments:
            original_counts[segment.osm_type] = (
                original_counts.get(segment.osm_type, 0) + 1
            )

        sample_counts = {}
        for segment in sample:
            sample_counts[segment.osm_type] = sample_counts.get(segment.osm_type, 0) + 1

        # Each type should be represented proportionally (within rounding)
        for road_type in original_types:
            expected_proportion = original_counts[road_type] / len(self.test_segments)
            actual_count = sample_counts.get(road_type, 0)
            actual_proportion = actual_count / len(sample)

            # Allow some tolerance for rounding
            self.assertAlmostEqual(actual_proportion, expected_proportion, delta=0.15)

    def test_stratified_sampling_edge_cases(self):
        """Test edge cases for stratified sampling."""
        # Sample size larger than population
        with self.assertRaises(ValueError):
            self.sampler.stratified_sample(100)

        # Stratified sampling with seed reproducibility
        sample1 = self.sampler.stratified_sample(15, seed=42)
        sample2 = self.sampler.stratified_sample(15, seed=42)
        self.assertEqual(sample1, sample2)

    def test_road_type_filtering(self):
        """Test filtering by road types in sampling."""
        # Filter by single road type
        primary_sample = self.sampler.random_sample(5, road_types="primary", seed=42)
        self.assertEqual(len(primary_sample), 5)
        self.assertTrue(all(s.osm_type == "primary" for s in primary_sample))

        # Filter by multiple road types
        multi_sample = self.sampler.random_sample(
            10, road_types=["primary", "secondary"], seed=42
        )
        self.assertEqual(len(multi_sample), 10)
        self.assertTrue(
            all(s.osm_type in ["primary", "secondary"] for s in multi_sample)
        )

        # Filter by non-existent road type should raise error (no segments available)
        with self.assertRaises(ValueError):
            self.sampler.random_sample(5, road_types=["nonexistent"], seed=42)

        # But requesting 0 segments should work
        empty_sample = self.sampler.random_sample(
            0, road_types=["nonexistent"], seed=42
        )
        self.assertEqual(len(empty_sample), 0)

        # Test filtering in stratified sampling
        filtered_stratified = self.sampler.stratified_sample(
            6, road_types=["primary", "secondary"], seed=42
        )
        self.assertEqual(len(filtered_stratified), 6)
        self.assertTrue(
            all(s.osm_type in ["primary", "secondary"] for s in filtered_stratified)
        )

    def test_sample_by_length(self):
        """Test sampling by target length."""
        # Sample for specific length (assumes 0.5km segments)
        length_sample = self.sampler.sample_by_length(2.5, seed=42)  # 5 segments
        self.assertEqual(len(length_sample), 5)

        # Length requiring more segments than available
        long_sample = self.sampler.sample_by_length(
            100.0, seed=42
        )  # Much longer than available
        self.assertEqual(len(long_sample), 50)  # Should return all available

        # Very short length
        short_sample = self.sampler.sample_by_length(0.5, seed=42)  # 1 segment
        self.assertEqual(len(short_sample), 1)

        # Zero length
        zero_sample = self.sampler.sample_by_length(0.0, seed=42)
        self.assertEqual(len(zero_sample), 0)

    def test_road_type_summary(self):
        """Test road type summary generation."""
        summary = self.sampler.get_road_type_summary()

        # Should be a dictionary
        self.assertIsInstance(summary, dict)

        # Should contain all road types from test data
        expected_types = {"primary", "secondary", "tertiary", "residential", "trunk"}
        self.assertEqual(set(summary.keys()), expected_types)

        # Each type should have count of 10 (50 segments / 5 types)
        for road_type, count in summary.items():
            self.assertEqual(count, 10)

        # Total count should equal original segment count
        self.assertEqual(sum(summary.values()), 50)

        # Test with filtering
        filtered_summary = self.sampler.get_road_type_summary(
            road_types=["primary", "secondary"]
        )
        self.assertEqual(set(filtered_summary.keys()), {"primary", "secondary"})
        self.assertEqual(sum(filtered_summary.values()), 20)

    def test_csv_operations(self):
        """Test CSV save and load operations."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            temp_path = temp_file.name

        try:
            # Save sample to CSV
            sample = self.sampler.random_sample(10, seed=42)
            self.sampler.save_csv(sample, temp_path)

            # Check file exists
            self.assertTrue(os.path.exists(temp_path))

            # Load back from CSV
            loaded_segments = load_segments_from_csv(temp_path)

            # Verify loaded data
            self.assertEqual(len(loaded_segments), 10)
            self.assertTrue(all(isinstance(s, RoadSegment) for s in loaded_segments))

            # Check data integrity
            for original, loaded in zip(sample, loaded_segments):
                self.assertEqual(original.segment_id, loaded.segment_id)
                self.assertEqual(original.osm_id, loaded.osm_id)
                self.assertEqual(original.osm_name, loaded.osm_name)
                self.assertEqual(original.osm_type, loaded.osm_type)
                self.assertAlmostEqual(original.start_lat, loaded.start_lat, places=6)
                self.assertAlmostEqual(original.start_long, loaded.start_long, places=6)
                self.assertAlmostEqual(original.end_lat, loaded.end_lat, places=6)
                self.assertAlmostEqual(original.end_long, loaded.end_long, places=6)

        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_plotting_functionality(self):
        """Test plotting functionality using real matplotlib."""
        sample = self.sampler.random_sample(5, seed=42)

        try:
            # Test basic sample plotting
            plt.figure()
            self.sampler.plot_sample(sample)
            plt.close()

            # Test comparison plotting
            plt.figure()
            self.sampler.plot_sample(sample, show_comparison=True)
            plt.close()

            # Test plotting without comparison
            plt.figure()
            self.sampler.plot_sample(sample, show_comparison=False)
            plt.close()

            # If we get here, plotting worked without errors
            self.assertTrue(True, "Plotting functionality works")

        except Exception as e:
            self.fail(f"Plotting functionality failed: {e}")

    def test_dataframe_conversion(self):
        """Test pandas DataFrame conversion using real pandas."""
        sample = self.sampler.random_sample(5, seed=42)

        try:
            import pandas as pd

            # Test DataFrame conversion
            result = self.sampler.to_dataframe(sample)

            # Should be a pandas DataFrame
            self.assertIsInstance(result, pd.DataFrame)

            # Should have correct number of rows
            self.assertEqual(len(result), 5)

            # Should have expected columns
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
            self.assertEqual(set(result.columns), expected_columns)

            # Check data types
            self.assertEqual(result["segment_id"].dtype, "int64")
            self.assertEqual(result["osm_id"].dtype, "object")
            self.assertTrue(result["start_lat"].dtype in ["float64", "float32"])

        except ImportError:
            # Skip this test if pandas is not available
            self.skipTest("pandas not available for testing")


class TestSamplingUtilityFunctions(unittest.TestCase):
    """Test utility functions for sampling."""

    def setUp(self):
        """Set up test data."""
        self.test_segments = [
            RoadSegment(
                i,
                f"way_{i}",
                f"Road {i}",
                "primary",
                1.0 + i * 0.001,
                103.0 + i * 0.001,
                1.0 + (i + 1) * 0.001,
                103.0 + (i + 1) * 0.001,
            )
            for i in range(20)
        ]

    def test_load_segments_from_csv(self):
        """Test loading segments from CSV file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".csv", delete=False
        ) as temp_file:
            # Write test CSV
            temp_file.write(
                "segment_id,osm_id,osm_name,osm_type,start_lat,start_long,end_lat,end_long\n"
            )
            temp_file.write("1,way_1,Test Road,primary,1.0,103.0,1.1,103.1\n")
            temp_file.write("2,way_2,Another Road,secondary,1.1,103.1,1.2,103.2\n")
            temp_path = temp_file.name

        try:
            segments = load_segments_from_csv(temp_path)

            self.assertEqual(len(segments), 2)
            self.assertTrue(all(isinstance(s, RoadSegment) for s in segments))

            # Check first segment
            first = segments[0]
            self.assertEqual(first.segment_id, 1)
            self.assertEqual(first.osm_id, "way_1")
            self.assertEqual(first.osm_name, "Test Road")
            self.assertEqual(first.osm_type, "primary")

        finally:
            os.unlink(temp_path)

    def test_sample_roads_convenience_function(self):
        """Test convenience sample_roads function."""
        # Random sampling
        random_sample = sample_roads(
            self.test_segments, n=5, strategy="random", seed=42
        )
        self.assertEqual(len(random_sample), 5)
        self.assertTrue(all(isinstance(s, RoadSegment) for s in random_sample))

        # Stratified sampling
        stratified_sample = sample_roads(
            self.test_segments, n=5, strategy="stratified", seed=42
        )
        self.assertEqual(len(stratified_sample), 5)

        # Invalid strategy should raise error
        with self.assertRaises(ValueError):
            sample_roads(self.test_segments, n=5, strategy="invalid")

        # Test with road type filtering
        filtered_sample = sample_roads(
            self.test_segments, n=3, road_types=["primary"], strategy="random", seed=42
        )
        self.assertEqual(len(filtered_sample), 3)
        self.assertTrue(all(s.osm_type == "primary" for s in filtered_sample))


class TestSamplingStatistics(unittest.TestCase):
    """Test statistical properties of sampling methods."""

    def setUp(self):
        """Set up test data with known distribution."""
        self.segments = []
        # Create 100 segments: 60 primary, 30 secondary, 10 tertiary
        for i in range(60):
            self.segments.append(
                RoadSegment(
                    i, f"way_{i}", f"Road {i}", "primary", 1.0, 103.0, 1.1, 103.1
                )
            )
        for i in range(30):
            self.segments.append(
                RoadSegment(
                    60 + i,
                    f"way_{60 + i}",
                    f"Road {60 + i}",
                    "secondary",
                    1.0,
                    103.0,
                    1.1,
                    103.1,
                )
            )
        for i in range(10):
            self.segments.append(
                RoadSegment(
                    90 + i,
                    f"way_{90 + i}",
                    f"Road {90 + i}",
                    "tertiary",
                    1.0,
                    103.0,
                    1.1,
                    103.1,
                )
            )

        self.sampler = RoadSampler(self.segments)

    def test_random_sampling_distribution(self):
        """Test that random sampling produces reasonable distributions."""
        # Take multiple samples and check distribution
        samples = []
        for _ in range(10):
            sample = self.sampler.random_sample(30, seed=None)  # Different seeds
            samples.extend(sample)

        # Count road types in combined samples
        type_counts = {}
        for segment in samples:
            type_counts[segment.osm_type] = type_counts.get(segment.osm_type, 0) + 1

        total_samples = len(samples)

        # Check proportions are roughly correct (within reasonable bounds)
        primary_proportion = type_counts.get("primary", 0) / total_samples
        secondary_proportion = type_counts.get("secondary", 0) / total_samples
        tertiary_proportion = type_counts.get("tertiary", 0) / total_samples

        # Expected: 60%, 30%, 10% - allow significant variance for random sampling
        self.assertGreater(primary_proportion, 0.4)  # Should be majority
        self.assertGreater(secondary_proportion, 0.1)  # Should have some
        self.assertGreater(tertiary_proportion, 0.02)  # Should have a few

    def test_stratified_sampling_proportions(self):
        """Test that stratified sampling maintains proportions."""
        sample = self.sampler.stratified_sample(30, seed=42)

        # Count types in sample
        sample_counts = {}
        for segment in sample:
            sample_counts[segment.osm_type] = sample_counts.get(segment.osm_type, 0) + 1

        # Calculate proportions
        primary_prop = sample_counts.get("primary", 0) / 30
        secondary_prop = sample_counts.get("secondary", 0) / 30
        tertiary_prop = sample_counts.get("tertiary", 0) / 30

        # Expected proportions: 0.6, 0.3, 0.1
        # Allow for rounding tolerance
        self.assertAlmostEqual(primary_prop, 0.6, delta=0.1)
        self.assertAlmostEqual(secondary_prop, 0.3, delta=0.1)
        self.assertAlmostEqual(tertiary_prop, 0.1, delta=0.1)


if __name__ == "__main__":
    unittest.main(verbosity=2)
