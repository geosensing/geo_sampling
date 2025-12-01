"""GADM (Global Administrative Areas) data provider."""

import os
import zipfile
from typing import List, Tuple, Optional
from urllib.parse import urljoin

import requests
import shapefile
from shapely.geometry import Polygon
from shapely.ops import unary_union

from .._types import BoundingBox


class GADMProvider:
    """Provider for GADM administrative boundary data."""

    GADM_BASE_URL = "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/"
    GADM_URL_FORMAT = "gadm41_{0}_shp.zip"

    def __init__(self, data_dir: str = "data"):
        """Initialize GADM provider.

        Args:
            data_dir: Directory to store downloaded data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)

    def get_country_list(self) -> List[str]:
        """Get list of available countries from GADM.

        Returns:
            List of country names
        """
        try:
            response = requests.get(
                "https://gadm.org/download_country.html", timeout=30
            )
            response.raise_for_status()

            # Extract country codes from HTML
            # This is a simplified version - in practice you'd parse the HTML properly
            countries = []
            for line in response.text.split("\n"):
                if "option value=" in line and "selected" not in line:
                    # Extract country name from HTML option
                    start = line.find(">") + 1
                    end = line.find("<", start)
                    if start > 0 and end > start:
                        country = line[start:end].strip()
                        if country and country != "Select country":
                            countries.append(country)

            return sorted(countries)

        except Exception as e:
            print(f"Warning: Could not fetch country list: {e}")
            return []

    def download_country_data(self, country_code: str) -> str:
        """Download GADM shapefile data for a country.

        Args:
            country_code: Three-letter country code (e.g., 'IND')

        Returns:
            Path to the downloaded and extracted directory
        """
        filename = self.GADM_URL_FORMAT.format(country_code)
        url = urljoin(self.GADM_BASE_URL, filename)

        local_zip_path = os.path.join(self.data_dir, filename)
        extract_dir = os.path.join(self.data_dir, country_code)

        # Download if not already present
        if not os.path.exists(local_zip_path):
            print(f"Downloading {url}...")
            self._download_file(url, local_zip_path)

        # Extract if not already done
        if not os.path.exists(extract_dir):
            print(f"Extracting {filename}...")
            with zipfile.ZipFile(local_zip_path, "r") as zip_ref:
                zip_ref.extractall(extract_dir)

        return extract_dir

    def load_boundaries(
        self, country_code: str, admin_level: int, region_name: Optional[str] = None
    ) -> Tuple[List[str], Polygon, BoundingBox]:
        """Load administrative boundaries for a country/region.

        Args:
            country_code: Three-letter country code
            admin_level: Administrative level (1-4)
            region_name: Specific region name to filter by

        Returns:
            Tuple of (region_names, combined_polygon, bounding_box)
        """
        extract_dir = self.download_country_data(country_code)
        shapefile_path = os.path.join(
            extract_dir, f"gadm41_{country_code}_{admin_level}"
        )

        if not os.path.exists(f"{shapefile_path}.shp"):
            raise FileNotFoundError(f"Shapefile not found: {shapefile_path}.shp")

        # Load shapefile
        sf = shapefile.Reader(shapefile_path)

        # Get field names to find the appropriate name field
        field_names = [field[0] for field in sf.fields[1:]]  # Skip DeletionFlag
        name_field = f"NAME_{admin_level}"

        if name_field not in field_names:
            # Fallback to other possible name fields
            for field in ["NAME_EN", "NAME", "NAME_1", "NAME_2"]:
                if field in field_names:
                    name_field = field
                    break

        region_names = []
        polygons = []

        # Process each shape record
        for record in sf.iterShapeRecords():
            shape = record.shape
            rec = record.record

            # Get region name
            try:
                name_index = field_names.index(name_field)
                current_name = rec[name_index]
            except (ValueError, IndexError):
                current_name = "Unknown"

            # Filter by region name if specified
            if region_name and region_name.lower() not in current_name.lower():
                continue

            region_names.append(current_name)

            # Convert shape to Shapely polygon
            if shape.shapeType == 5:  # Polygon
                polygons.append(Polygon(shape.points))
            elif shape.shapeType == 15:  # PolygonZ
                polygons.append(Polygon([(x, y) for x, y, z in shape.points]))

        if not polygons:
            if region_name:
                raise ValueError(
                    f"Region '{region_name}' not found in {country_code} level {admin_level}"
                )
            else:
                raise ValueError(
                    f"No boundaries found for {country_code} level {admin_level}"
                )

        # Combine all polygons
        combined_polygon = unary_union(polygons)

        # Calculate bounding box
        bounds = combined_polygon.bounds
        bbox = BoundingBox(
            min_long=bounds[0], min_lat=bounds[1], max_long=bounds[2], max_lat=bounds[3]
        )

        return region_names, combined_polygon, bbox

    def _download_file(self, url: str, local_path: str) -> None:
        """Download a file from URL to local path."""
        response = requests.get(url, timeout=30, stream=True)
        response.raise_for_status()

        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
