#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
End-to-end integration tests for geo_sampling.

These tests validate the complete user workflow from extraction to sampling
and plotting. They use Singapore as a test region for speed and reliability.
"""

import os
import shutil
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch
import matplotlib

matplotlib.use("Agg")  # Use non-interactive backend for testing
import matplotlib.pyplot as plt

import geo_sampling as gs
from geo_sampling._types import RoadSegment


class TestE2EIntegration(unittest.TestCase):
    """End-to-end integration tests for the complete workflow."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment once for all tests."""
        cls.test_dir = tempfile.mkdtemp()
        cls.country = "Singapore"
        cls.region = "Central"
        cls.admin_level = 1

    @classmethod
    def tearDownClass(cls):
        """Clean up test environment."""
        if os.path.exists(cls.test_dir):
            shutil.rmtree(cls.test_dir)

    def setUp(self):
        """Set up each test."""
        # Change to test directory for each test
        self.original_cwd = os.getcwd()
        os.chdir(self.test_dir)

    def tearDown(self):
        """Clean up each test."""
        os.chdir(self.original_cwd)
        # Clean up any data directories created during tests
        if os.path.exists(os.path.join(self.test_dir, "data")):
            shutil.rmtree(os.path.join(self.test_dir, "data"))

    @unittest.skip("Requires network access - enable for full integration testing")
    def test_full_workflow_real_data(self):
        """Test complete workflow with real Singapore data (network required)."""
        # This test is skipped by default but can be enabled for manual testing
        extractor = gs.RoadExtractor(self.country, self.region, self.admin_level)

        # Extract roads
        roads = extractor.get_roads()

        # Validate extracted data
        self.assertGreater(len(roads), 0, "Should extract some road segments")
        self.assertTrue(
            all(isinstance(r, RoadSegment) for r in roads),
            "All extracted items should be RoadSegment objects",
        )

        # Test road type filtering
        if len(roads) > 10:  # Only test if we have enough data
            available_types = extractor.get_available_road_types()
            self.assertGreater(len(available_types), 0, "Should have some road types")

            # Filter by road type
            filtered_roads = extractor.get_roads(road_types=[available_types[0]])
            self.assertGreater(
                len(filtered_roads), 0, "Filtered roads should not be empty"
            )
            self.assertTrue(
                all(r.osm_type == available_types[0] for r in filtered_roads),
                "All filtered roads should match the specified type",
            )

        # Test sampling
        sample_size = min(10, len(roads))
        sampler = gs.RoadSampler(roads)

        # Random sampling
        random_sample = sampler.random_sample(sample_size, seed=42)
        self.assertEqual(
            len(random_sample), sample_size, "Sample should have requested size"
        )

        # Stratified sampling (if we have multiple road types)
        if len(sampler.get_road_type_summary()) > 1:
            stratified_sample = sampler.stratified_sample(sample_size, seed=42)
            self.assertEqual(
                len(stratified_sample),
                sample_size,
                "Stratified sample should have requested size",
            )

        # Test CSV save/load
        csv_path = "test_roads.csv"
        sampler.save_csv(random_sample, csv_path)
        self.assertTrue(os.path.exists(csv_path), "CSV file should be created")

        # Load and verify
        loaded_segments = gs.load_segments_from_csv(csv_path)
        self.assertEqual(
            len(loaded_segments),
            len(random_sample),
            "Loaded segments should match saved segments",
        )
        self.assertTrue(
            all(isinstance(r, RoadSegment) for r in loaded_segments),
            "Loaded segments should be RoadSegment objects",
        )

    def test_workflow_with_mocked_data(self):
        """Test workflow with mocked external data for fast, reliable testing."""
        # Create mock road segments
        mock_segments = [
            RoadSegment(
                segment_id=i,
                osm_id=f"way_{i}",
                osm_name=f"Road {i}",
                osm_type="primary" if i % 2 == 0 else "secondary",
                start_lat=1.3521 + i * 0.001,
                start_long=103.8198 + i * 0.001,
                end_lat=1.3521 + (i + 1) * 0.001,
                end_long=103.8198 + (i + 1) * 0.001,
            )
            for i in range(20)
        ]

        # Mock the RoadExtractor to return our test data
        with patch.object(gs.RoadExtractor, "get_roads", return_value=mock_segments):
            # Test high-level convenience function
            sample = gs.sample_roads_for_region(self.country, self.region, n=5, seed=42)

            self.assertEqual(len(sample), 5, "Should return requested sample size")
            self.assertTrue(
                all(isinstance(s, RoadSegment) for s in sample),
                "All samples should be RoadSegment objects",
            )

            # Test that we can access all segment attributes
            for segment in sample:
                self.assertIsInstance(segment.segment_id, int)
                self.assertIsInstance(segment.osm_id, str)
                self.assertIsInstance(segment.osm_name, str)
                self.assertIsInstance(segment.osm_type, str)
                self.assertIsInstance(segment.start_lat, float)
                self.assertIsInstance(segment.start_long, float)
                self.assertIsInstance(segment.end_lat, float)
                self.assertIsInstance(segment.end_long, float)

    def test_sampler_functionality(self):
        """Test RoadSampler with various sampling strategies."""
        # Create test data with multiple road types
        test_segments = []
        for i in range(50):
            road_type = ["primary", "secondary", "tertiary"][i % 3]
            test_segments.append(
                RoadSegment(
                    segment_id=i,
                    osm_id=f"way_{i}",
                    osm_name=f"Test Road {i}",
                    osm_type=road_type,
                    start_lat=1.3 + i * 0.001,
                    start_long=103.8 + i * 0.001,
                    end_lat=1.3 + (i + 1) * 0.001,
                    end_long=103.8 + (i + 1) * 0.001,
                )
            )

        sampler = gs.RoadSampler(test_segments)

        # Test random sampling
        random_sample = sampler.random_sample(10, seed=42)
        self.assertEqual(len(random_sample), 10)

        # Test stratified sampling
        stratified_sample = sampler.stratified_sample(15, seed=42)
        self.assertEqual(len(stratified_sample), 15)

        # Test road type filtering
        primary_sample = sampler.random_sample(5, road_types=["primary"], seed=42)
        self.assertEqual(len(primary_sample), 5)
        self.assertTrue(all(s.osm_type == "primary" for s in primary_sample))

        # Test sampling by length
        length_sample = sampler.sample_by_length(2.5, seed=42)  # 2.5km = 5 segments
        self.assertEqual(len(length_sample), 5)

        # Test road type summary
        summary = sampler.get_road_type_summary()
        self.assertIn("primary", summary)
        self.assertIn("secondary", summary)
        self.assertIn("tertiary", summary)
        self.assertEqual(sum(summary.values()), 50)

    def test_plotting_functionality(self):
        """Test plotting functionality without displaying plots."""
        # Create test segments
        test_segments = [
            RoadSegment(
                segment_id=1,
                osm_id="way_1",
                osm_name="Test Road 1",
                osm_type="primary",
                start_lat=1.3521,
                start_long=103.8198,
                end_lat=1.3531,
                end_long=103.8208,
            ),
            RoadSegment(
                segment_id=2,
                osm_id="way_2",
                osm_name="Test Road 2",
                osm_type="secondary",
                start_lat=1.3531,
                start_long=103.8208,
                end_lat=1.3541,
                end_long=103.8218,
            ),
        ]

        # Test plotting functionality using real matplotlib (non-interactive backend)
        try:
            # Test plotting segments
            plt.figure()
            gs.plot_road_segments(test_segments, title="Test Plot")
            plt.close()  # Close figure to prevent display

            # Test RoadPlotter
            plt.figure()
            plotter = gs.RoadPlotter()
            plotter.plot(test_segments, title="Direct Plotter Test")
            plt.close()

            # Test sampler plotting
            plt.figure()
            sampler = gs.RoadSampler(test_segments)
            sampler.plot_sample(test_segments)
            plt.close()

            # If we get here, plotting worked without errors
            self.assertTrue(True, "Plotting functionality works")

        except Exception as e:
            self.fail(f"Plotting functionality failed: {e}")

    def test_csv_operations(self):
        """Test CSV save and load operations."""
        # Create test segments
        test_segments = [
            RoadSegment(
                segment_id=1,
                osm_id="way_1",
                osm_name="Test Road",
                osm_type="primary",
                start_lat=1.3521,
                start_long=103.8198,
                end_lat=1.3531,
                end_long=103.8208,
            )
        ]

        # Test saving to CSV
        csv_path = "test_segments.csv"
        sampler = gs.RoadSampler(test_segments)
        sampler.save_csv(test_segments, csv_path)

        self.assertTrue(os.path.exists(csv_path), "CSV file should be created")

        # Test loading from CSV
        loaded_segments = gs.load_segments_from_csv(csv_path)

        self.assertEqual(len(loaded_segments), 1, "Should load one segment")
        loaded_segment = loaded_segments[0]
        original_segment = test_segments[0]

        # Check all fields match
        self.assertEqual(loaded_segment.segment_id, original_segment.segment_id)
        self.assertEqual(loaded_segment.osm_id, original_segment.osm_id)
        self.assertEqual(loaded_segment.osm_name, original_segment.osm_name)
        self.assertEqual(loaded_segment.osm_type, original_segment.osm_type)
        self.assertAlmostEqual(
            loaded_segment.start_lat, original_segment.start_lat, places=6
        )
        self.assertAlmostEqual(
            loaded_segment.start_long, original_segment.start_long, places=6
        )
        self.assertAlmostEqual(
            loaded_segment.end_lat, original_segment.end_lat, places=6
        )
        self.assertAlmostEqual(
            loaded_segment.end_long, original_segment.end_long, places=6
        )

    def test_cli_interface(self):
        """Test CLI commands work correctly."""
        # Test CLI help commands work
        result = subprocess.run(
            [sys.executable, "-m", "geo_sampling.cli", "--help"],
            capture_output=True,
            text=True,
            cwd=self.test_dir,
        )

        self.assertEqual(result.returncode, 0, "CLI help should work")
        self.assertIn("geo_sampling", result.stdout, "Help should mention package name")

        # Test individual command help
        result = subprocess.run(
            [sys.executable, "-m", "geo_sampling.cli", "workflow", "--help"],
            capture_output=True,
            text=True,
            cwd=self.test_dir,
        )

        self.assertEqual(result.returncode, 0, "Workflow help should work")
        self.assertIn("workflow", result.stdout, "Help should mention workflow command")

    def test_error_handling(self):
        """Test proper error handling for edge cases."""
        # Test sampling more than available
        small_segments = [
            RoadSegment(1, "way_1", "Road 1", "primary", 1.0, 103.0, 1.1, 103.1)
        ]

        sampler = gs.RoadSampler(small_segments)

        with self.assertRaises(ValueError):
            sampler.random_sample(5)  # More than available

        # Test empty segments
        with self.assertRaises(ValueError):
            gs.RoadSampler([])  # Empty list

        # Test invalid road types in filtering - should raise error for non-zero sample size
        with self.assertRaises(ValueError):
            sampler.random_sample(1, road_types=["nonexistent"])

        # But zero sample size should work
        filtered = sampler.random_sample(0, road_types=["nonexistent"])
        self.assertEqual(
            len(filtered), 0, "Should return empty list for zero sample size"
        )


if __name__ == "__main__":
    # Run with verbose output
    unittest.main(verbosity=2)
