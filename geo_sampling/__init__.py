"""geo_sampling: Extract and sample road segments from OpenStreetMap data.

This package provides tools for randomly sampling street locations for data
collection by downloading OpenStreetMap data and processing road segments.

Basic usage:
    >>> import geo_sampling as gs
    >>>
    >>> # Quick workflow - extract and sample in one step
    >>> sample = gs.sample_roads_for_region("India", "NCT of Delhi", n=1000)
    >>>
    >>> # Step-by-step with more control
    >>> extractor = gs.RoadExtractor("India", "NCT of Delhi")
    >>> roads = extractor.get_roads(road_types=["primary", "secondary"])
    >>> sampler = gs.RoadSampler(roads)
    >>> sample = sampler.random_sample(500)
    >>> sample.plot()

For more examples, see the documentation at:
https://geosensing.github.io/geo_sampling/
"""

__version__ = "0.3.0"
__author__ = "Suriyan Laohaprapanon, Gaurav Sood"
__email__ = "gsood07@gmail.com"

# Import main classes and functions for easy access
from .extractor import RoadExtractor, extract_roads
from .sampler import RoadSampler, load_segments_from_csv, sample_roads
from ._types import RoadSegment, BoundingBox
from .visualization import plot_road_segments, RoadPlotter
from .convenience import (
    sample_roads_for_region,
    extract_and_save,
    sample_and_save,
    quick_plot,
    get_road_summary,
)

# Import data providers for advanced usage
from .data import GADMProvider, OSMProvider

__all__ = [
    # Main classes
    "RoadExtractor",
    "RoadSampler",
    "RoadPlotter",
    # Data types
    "RoadSegment",
    "BoundingBox",
    # High-level convenience functions
    "sample_roads_for_region",
    "extract_and_save",
    "sample_and_save",
    "quick_plot",
    "get_road_summary",
    # Core functions
    "extract_roads",
    "sample_roads",
    "load_segments_from_csv",
    "plot_road_segments",
    # Data providers (advanced)
    "GADMProvider",
    "OSMProvider",
]
