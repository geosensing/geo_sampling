"""Data provider modules for GADM and OSM data."""

from .gadm import GADMProvider
from .osm import OSMProvider

__all__ = ["GADMProvider", "OSMProvider"]
