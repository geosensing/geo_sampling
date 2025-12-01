"""OpenStreetMap data provider via BBBike.org."""

import os
import time
import zipfile
from typing import List, Tuple, Optional
from urllib.parse import urlencode

import requests
from bs4 import BeautifulSoup
import shapefile
from shapely.geometry import Polygon, LineString
import pyproj
import utm

from .._types import BoundingBox, RoadSegment


class OSMProvider:
    """Provider for OpenStreetMap data via BBBike.org extract service."""
    
    BBBIKE_BASE_URL = "http://extract.bbbike.org"
    MAX_EXTRACT_POINTS = 300
    MAX_WAIT_TIME = 50  # seconds
    
    def __init__(self, data_dir: str = "data"):
        """Initialize OSM provider.
        
        Args:
            data_dir: Directory to store downloaded data
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
    
    def generate_extract_url(self, region_polygon: Polygon, region_name: str, 
                           bbox: BoundingBox) -> str:
        """Generate BBBike extract URL for a polygon region.
        
        Args:
            region_polygon: Shapely polygon defining the region
            region_name: Name for the extract
            bbox: Bounding box coordinates
            
        Returns:
            BBBike extract URL
        """
        # Simplify polygon to reduce points if needed
        simplified_polygon = self._simplify_polygon_for_bbbike(region_polygon)
        
        # Convert polygon to coordinate string format
        coords = []
        for x, y in simplified_polygon.exterior.coords[:-1]:  # Skip last duplicate point
            coords.append(f"{x:.3f},{y:.3f}")
        
        # Build URL parameters
        params = {
            'sw_lng': bbox.min_long,
            'sw_lat': bbox.min_lat,
            'ne_lng': bbox.max_long, 
            'ne_lat': bbox.max_lat,
            'coords': '|'.join(coords),
            'format': 'shp.zip',
            'city': region_name.lower().replace(' ', '_')
        }
        
        return f"{self.BBBIKE_BASE_URL}/?{urlencode(params)}"
    
    def submit_extract_request(self, extract_url: str) -> str:
        """Submit extract request to BBBike and get job ID.
        
        Args:
            extract_url: BBBike extract URL
            
        Returns:
            Extract job ID for checking status
        """
        print(f"Submitting extract request...")
        response = requests.get(extract_url, timeout=30)
        response.raise_for_status()
        
        # Parse response to get extract ID
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Look for extract ID in various possible locations
        extract_id = None
        
        # Check for redirect or confirmation page
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'extract' in href and 'id=' in href:
                # Extract ID from URL parameter
                extract_id = href.split('id=')[1].split('&')[0]
                break
        
        if not extract_id:
            # Look for extract ID in text
            text = response.text
            if 'extract/' in text:
                for line in text.split('\n'):
                    if 'extract/' in line:
                        # Try to extract ID from line
                        parts = line.split('extract/')
                        if len(parts) > 1:
                            extract_id = parts[1].split('/')[0].split('"')[0]
                            break
        
        if not extract_id:
            raise RuntimeError("Could not determine extract ID from BBBike response")
        
        print(f"Extract job submitted with ID: {extract_id}")
        return extract_id
    
    def check_extract_status(self, extract_id: str) -> Optional[str]:
        """Check status of BBBike extract job.
        
        Args:
            extract_id: Job ID from submit_extract_request
            
        Returns:
            Download URL if ready, None if still processing
        """
        status_url = f"http://download.bbbike.org/osm/extract/{extract_id}/"
        
        try:
            response = requests.get(status_url, timeout=10)
            response.raise_for_status()
            
            # Look for download links
            soup = BeautifulSoup(response.text, 'html.parser')
            
            for link in soup.find_all('a', href=True):
                href = link['href']
                if href.endswith('.zip') and 'shp' in href:
                    # Found download link
                    download_url = f"http://download.bbbike.org{href}" if href.startswith('/') else href
                    return download_url
            
            return None  # Still processing
            
        except Exception as e:
            print(f"Warning: Could not check extract status: {e}")
            return None
    
    def download_osm_data(self, region_polygon: Polygon, region_name: str, 
                         bbox: BoundingBox) -> str:
        """Download OSM data for a region and return path to road shapefile.
        
        Args:
            region_polygon: Shapely polygon defining region
            region_name: Name for the extract
            bbox: Bounding box coordinates
            
        Returns:
            Path to the roads shapefile (without .shp extension)
        """
        # Generate extract URL
        extract_url = self.generate_extract_url(region_polygon, region_name, bbox)
        print(f"Extract URL: {extract_url}")
        
        # Submit extract request
        extract_id = self.submit_extract_request(extract_url)
        
        # Wait for extract to complete
        print("Waiting for extract to complete...")
        download_url = None
        
        for attempt in range(self.MAX_WAIT_TIME):
            download_url = self.check_extract_status(extract_id)
            if download_url:
                break
            time.sleep(1)
        
        if not download_url:
            raise TimeoutError(f"Extract did not complete within {self.MAX_WAIT_TIME} seconds")
        
        # Download and extract data
        print(f"Downloading from: {download_url}")
        zip_filename = f"{region_name.replace(' ', '_')}_osm.zip"
        zip_path = os.path.join(self.data_dir, zip_filename)
        
        self._download_file(download_url, zip_path)
        
        # Extract zip file
        extract_dir = os.path.join(self.data_dir, f"{region_name.replace(' ', '_')}_osm")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
        
        # Find roads shapefile
        roads_shapefile = os.path.join(extract_dir, "roads")
        if not os.path.exists(f"{roads_shapefile}.shp"):
            raise FileNotFoundError("Roads shapefile not found in extracted data")
        
        return roads_shapefile
    
    def extract_road_segments(self, shapefile_path: str, road_types: Optional[List[str]] = None,
                            segment_length: int = 500) -> List[RoadSegment]:
        """Extract road segments from OSM shapefile.
        
        Args:
            shapefile_path: Path to roads shapefile (without .shp)
            road_types: List of road types to include (None = all)
            segment_length: Target segment length in meters
            
        Returns:
            List of RoadSegment objects
        """
        sf = shapefile.Reader(shapefile_path)
        
        # Get field names
        field_names = [field[0] for field in sf.fields[1:]]
        
        segments = []
        segment_id = 1
        
        for record in sf.iterShapeRecords():
            shape = record.shape
            rec = record.record
            
            # Extract road metadata
            osm_id = str(rec[field_names.index('osm_id')] if 'osm_id' in field_names else '')
            osm_name = str(rec[field_names.index('name')] if 'name' in field_names else '')
            osm_type = str(rec[field_names.index('type')] if 'type' in field_names else 'unknown')
            
            # Filter by road type if specified
            if road_types and osm_type not in road_types:
                continue
            
            # Skip non-linestring shapes
            if shape.shapeType not in [3, 13]:  # Polyline, PolylineZ
                continue
            
            # Convert to LineString and split into segments
            if shape.shapeType == 3:  # Polyline
                line = LineString(shape.points)
            else:  # PolylineZ
                line = LineString([(x, y) for x, y, z in shape.points])
            
            # Split line into segments of specified length
            split_segments = self._split_linestring(line, segment_length)
            
            for segment_line in split_segments:
                coords = list(segment_line.coords)
                start_point = coords[0]
                end_point = coords[-1]
                
                segments.append(RoadSegment(
                    segment_id=segment_id,
                    osm_id=osm_id,
                    osm_name=osm_name,
                    osm_type=osm_type,
                    start_lat=start_point[1],
                    start_long=start_point[0],
                    end_lat=end_point[1], 
                    end_long=end_point[0]
                ))
                
                segment_id += 1
        
        return segments
    
    def _simplify_polygon_for_bbbike(self, polygon: Polygon) -> Polygon:
        """Simplify polygon to meet BBBike point limit."""
        if len(polygon.exterior.coords) <= self.MAX_EXTRACT_POINTS:
            return polygon
        
        # Progressively increase tolerance until we're under the limit
        tolerance = 0.001
        simplified = polygon
        
        while len(simplified.exterior.coords) > self.MAX_EXTRACT_POINTS and tolerance < 0.1:
            simplified = polygon.simplify(tolerance)
            tolerance *= 1.5
        
        return simplified
    
    def _split_linestring(self, line: LineString, segment_length: int) -> List[LineString]:
        """Split a LineString into segments of specified length."""
        if line.length == 0:
            return []
        
        # Convert to UTM for accurate distance calculations
        # Use the centroid to determine UTM zone
        centroid = line.centroid
        utm_zone, hemisphere = utm.from_latlon(centroid.y, centroid.x)[:2]
        
        # Create transformer to UTM
        utm_crs = f"+proj=utm +zone={utm_zone} +{'south' if hemisphere < 0 else 'north'} +datum=WGS84"
        transformer = pyproj.Transformer.from_crs("EPSG:4326", utm_crs, always_xy=True)
        
        # Transform to UTM
        utm_coords = [transformer.transform(x, y) for x, y in line.coords]
        utm_line = LineString(utm_coords)
        
        segments = []
        current_distance = 0
        total_length = utm_line.length
        
        while current_distance < total_length:
            # Get start point
            start_point = utm_line.interpolate(current_distance)
            
            # Get end point (or line end if remaining distance < segment_length)
            end_distance = min(current_distance + segment_length, total_length)
            end_point = utm_line.interpolate(end_distance)
            
            # Create segment
            segment = LineString([start_point.coords[0], end_point.coords[0]])
            
            # Transform back to WGS84
            wgs84_coords = []
            for x, y in segment.coords:
                lat, lon = utm.to_latlon(x, y, utm_zone, hemisphere)
                wgs84_coords.append((lon, lat))
            
            segments.append(LineString(wgs84_coords))
            current_distance = end_distance
        
        return segments
    
    def _download_file(self, url: str, local_path: str) -> None:
        """Download a file from URL to local path."""
        response = requests.get(url, timeout=60, stream=True)
        response.raise_for_status()
        
        with open(local_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)