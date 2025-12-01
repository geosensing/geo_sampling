"""Road extraction functionality."""

import csv
from typing import List, Optional, Union
from pathlib import Path

from ._types import RoadSegment, RoadTypeFilter
from .data import GADMProvider, OSMProvider
from .visualization import RoadPlotter


class RoadExtractor:
    """Main class for extracting road segments from OpenStreetMap data.

    This class handles the complete workflow:
    1. Download administrative boundaries from GADM
    2. Generate BBBike extract URLs
    3. Download OSM data
    4. Extract and segment roads
    """

    def __init__(
        self, country: str, region: str, admin_level: int = 1, data_dir: str = "data"
    ):
        """Initialize road extractor.

        Args:
            country: Country name (e.g., "India")
            region: Region name (e.g., "NCT of Delhi")
            admin_level: Administrative level (1-4)
            data_dir: Directory for caching downloaded data
        """
        self.country = country
        self.region = region
        self.admin_level = admin_level
        self.data_dir = data_dir

        # Initialize data providers
        self.gadm = GADMProvider(data_dir)
        self.osm = OSMProvider(data_dir)

        # Cached data
        self._road_segments: Optional[List[RoadSegment]] = None
        self._country_code: Optional[str] = None

    def get_roads(
        self,
        road_types: RoadTypeFilter = None,
        segment_length: int = 500,
        force_refresh: bool = False,
    ) -> List[RoadSegment]:
        """Extract road segments for the configured region.

        Args:
            road_types: Road types to include (None = all types)
            segment_length: Target segment length in meters
            force_refresh: Force re-download of data

        Returns:
            List of RoadSegment objects
        """
        # Use cached results if available and not forcing refresh
        if self._road_segments and not force_refresh:
            return self._filter_by_road_types(self._road_segments, road_types)

        print(f"Extracting roads for {self.region}, {self.country}...")

        # Step 1: Get country code and validate
        country_code = self._get_country_code()
        print(f"Using country code: {country_code}")

        # Step 2: Load administrative boundaries
        print(f"Loading administrative boundaries (level {self.admin_level})...")
        region_names, region_polygon, bbox = self.gadm.load_boundaries(
            country_code, self.admin_level, self.region
        )
        print(f"Found regions: {region_names}")
        print(
            f"Bounding box: {bbox.min_lat:.3f}, {bbox.min_long:.3f} to {bbox.max_lat:.3f}, {bbox.max_long:.3f}"
        )

        # Step 3: Download OSM data
        print("Downloading OSM data from BBBike...")
        roads_shapefile = self.osm.download_osm_data(region_polygon, self.region, bbox)
        print(f"OSM data downloaded to: {roads_shapefile}")

        # Step 4: Extract road segments
        print("Extracting road segments...")
        self._road_segments = self.osm.extract_road_segments(
            roads_shapefile,
            road_types if isinstance(road_types, list) else None,
            segment_length,
        )
        print(f"Extracted {len(self._road_segments)} road segments")

        # Return filtered results
        return self._filter_by_road_types(self._road_segments, road_types)

    def get_available_road_types(self) -> List[str]:
        """Get list of available road types in the extracted data.

        Returns:
            Sorted list of unique road types
        """
        if not self._road_segments:
            self.get_roads()  # Extract roads first

        return sorted(set(segment.osm_type for segment in self._road_segments))

    def save_csv(
        self,
        path: Union[str, Path],
        road_types: RoadTypeFilter = None,
        segment_length: int = 500,
    ) -> None:
        """Save road segments to CSV file.

        Args:
            path: Output file path
            road_types: Road types to include
            segment_length: Target segment length in meters
        """
        segments = self.get_roads(road_types, segment_length)

        columns = [
            "segment_id",
            "osm_id",
            "osm_name",
            "osm_type",
            "start_lat",
            "start_long",
            "end_lat",
            "end_long",
        ]

        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=columns)
            writer.writeheader()
            for segment in segments:
                writer.writerow(segment.to_dict())

        print(f"Saved {len(segments)} segments to {path}")

    def plot(
        self,
        road_types: RoadTypeFilter = None,
        segment_length: int = 500,
        title: Optional[str] = None,
        figsize: tuple = (12, 10),
    ) -> None:
        """Plot the extracted road segments.

        Args:
            road_types: Road types to include
            segment_length: Target segment length in meters
            title: Plot title (auto-generated if None)
            figsize: Figure size
        """
        segments = self.get_roads(road_types, segment_length)

        if not title:
            title = (
                f"Road Segments: {self.region}, {self.country} (N = {len(segments)})"
            )

        plotter = RoadPlotter(figsize=figsize)
        plotter.plot(segments, title=title)

    def to_dataframe(
        self, road_types: RoadTypeFilter = None, segment_length: int = 500
    ):
        """Convert road segments to pandas DataFrame.

        Args:
            road_types: Road types to include
            segment_length: Target segment length in meters

        Returns:
            pandas.DataFrame with road segment data

        Raises:
            ImportError: If pandas is not installed
        """
        try:
            import pandas as pd
        except ImportError:
            raise ImportError(
                "pandas is required for DataFrame conversion. Install with: pip install pandas"
            )

        segments = self.get_roads(road_types, segment_length)
        data = [segment.to_dict() for segment in segments]

        return pd.DataFrame(data)

    def _get_country_code(self) -> str:
        """Get three-letter country code for the country."""
        if self._country_code:
            return self._country_code

        # Simple mapping for common countries
        # In a real implementation, you'd want a more comprehensive mapping
        country_codes = {
            "india": "IND",
            "united states": "USA",
            "usa": "USA",
            "thailand": "THA",
            "singapore": "SGP",
            "united kingdom": "GBR",
            "uk": "GBR",
            "canada": "CAN",
            "australia": "AUS",
            "china": "CHN",
            "japan": "JPN",
            "germany": "DEU",
            "france": "FRA",
            "italy": "ITA",
            "spain": "ESP",
            "brazil": "BRA",
            "mexico": "MEX",
        }

        country_lower = self.country.lower()
        if country_lower in country_codes:
            self._country_code = country_codes[country_lower]
            return self._country_code

        # Try first 3 letters as fallback
        self._country_code = self.country[:3].upper()
        print(
            f"Warning: Using fallback country code '{self._country_code}' for '{self.country}'"
        )
        return self._country_code

    def _filter_by_road_types(
        self, segments: List[RoadSegment], road_types: RoadTypeFilter
    ) -> List[RoadSegment]:
        """Filter segments by road types."""
        if not road_types:
            return segments

        # Convert single string to list
        if isinstance(road_types, str):
            road_types = [road_types]

        return [seg for seg in segments if seg.osm_type in road_types]


def extract_roads(
    country: str,
    region: str,
    admin_level: int = 1,
    road_types: RoadTypeFilter = None,
    segment_length: int = 500,
    data_dir: str = "data",
) -> List[RoadSegment]:
    """Convenience function to extract roads in one call.

    Args:
        country: Country name
        region: Region name
        admin_level: Administrative level
        road_types: Road types to include
        segment_length: Target segment length in meters
        data_dir: Data directory

    Returns:
        List of RoadSegment objects
    """
    extractor = RoadExtractor(country, region, admin_level, data_dir)
    return extractor.get_roads(road_types, segment_length)
