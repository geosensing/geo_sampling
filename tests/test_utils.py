#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Shared test utilities and data for geo_sampling tests.
"""

import tempfile
import csv
import os


class TestDataMixin:
    """Mixin providing common test data and utilities."""

    @property
    def sample_test_data(self):
        """Standard test data for road segments."""
        return [
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

    def create_test_csv(self, data=None):
        """Create a temporary CSV file with test data."""
        if data is None:
            data = self.sample_test_data

        temp_file = tempfile.NamedTemporaryFile(
            mode='w', delete=False, suffix='.csv'
        )

        with temp_file as temp_csv:
            writer = csv.DictWriter(temp_csv, fieldnames=[
                "segment_id", "osm_id", "osm_name", "osm_type",
                "start_lat", "start_long", "end_lat", "end_long"
            ])
            writer.writeheader()
            writer.writerows(data)

        return temp_file.name

    def cleanup_temp_file(self, filepath):
        """Safely clean up a temporary file."""
        if os.path.exists(filepath):
            os.unlink(filepath)
