"""High-level convenience functions for common workflows."""

from typing import List, Optional

from ._types import RoadSegment, RoadTypeFilter
from .extractor import RoadExtractor
from .sampler import RoadSampler


def sample_roads_for_region(
    country: str,
    region: str,
    n: int,
    admin_level: int = 1,
    road_types: RoadTypeFilter = None,
    segment_length: int = 500,
    strategy: str = "random",
    seed: Optional[int] = None,
    data_dir: str = "data",
) -> List[RoadSegment]:
    """One-liner function to extract and sample roads for a region.

    This function handles the complete workflow:
    1. Extract roads for the specified region
    2. Sample the requested number of segments

    Args:
        country: Country name (e.g., "India")
        region: Region name (e.g., "NCT of Delhi")
        n: Number of segments to sample
        admin_level: Administrative level (1-4)
        road_types: Road types to include (None = all types)
        segment_length: Target segment length in meters
        strategy: Sampling strategy ("random" or "stratified")
        seed: Random seed for reproducibility
        data_dir: Directory for caching downloaded data

    Returns:
        List of sampled RoadSegment objects

    Example:
        >>> segments = sample_roads_for_region(
        ...     "India", "NCT of Delhi", n=1000,
        ...     road_types=["primary", "secondary"]
        ... )
    """
    # Extract roads
    extractor = RoadExtractor(country, region, admin_level, data_dir)
    all_roads = extractor.get_roads(road_types, segment_length)

    # Sample roads
    sampler = RoadSampler(all_roads)

    if strategy == "random":
        return sampler.random_sample(n, seed=seed)
    elif strategy == "stratified":
        return sampler.stratified_sample(n, seed=seed)
    else:
        raise ValueError(f"Unknown sampling strategy: {strategy}")


def extract_and_save(
    country: str,
    region: str,
    output_path: str,
    admin_level: int = 1,
    road_types: RoadTypeFilter = None,
    segment_length: int = 500,
    data_dir: str = "data",
) -> List[RoadSegment]:
    """Extract roads and save directly to CSV.

    Args:
        country: Country name
        region: Region name
        output_path: Path for output CSV file
        admin_level: Administrative level
        road_types: Road types to include
        segment_length: Target segment length in meters
        data_dir: Directory for caching downloaded data

    Returns:
        List of extracted RoadSegment objects
    """
    extractor = RoadExtractor(country, region, admin_level, data_dir)
    extractor.save_csv(output_path, road_types, segment_length)

    # Return the segments that were saved
    return extractor.get_roads(road_types, segment_length)


def sample_and_save(
    country: str,
    region: str,
    output_path: str,
    n: int,
    admin_level: int = 1,
    road_types: RoadTypeFilter = None,
    segment_length: int = 500,
    strategy: str = "random",
    seed: Optional[int] = None,
    data_dir: str = "data",
) -> List[RoadSegment]:
    """Extract roads, sample, and save directly to CSV.

    Args:
        country: Country name
        region: Region name
        output_path: Path for output CSV file
        n: Number of segments to sample
        admin_level: Administrative level
        road_types: Road types to include
        segment_length: Target segment length in meters
        strategy: Sampling strategy ("random" or "stratified")
        seed: Random seed for reproducibility
        data_dir: Directory for caching downloaded data

    Returns:
        List of sampled RoadSegment objects
    """
    # Get sample
    sample = sample_roads_for_region(
        country,
        region,
        n,
        admin_level,
        road_types,
        segment_length,
        strategy,
        seed,
        data_dir,
    )

    # Save to CSV
    sampler = RoadSampler(sample)
    sampler.save_csv(sample, output_path)

    return sample


def quick_plot(
    country: str,
    region: str,
    n: Optional[int] = None,
    admin_level: int = 1,
    road_types: RoadTypeFilter = None,
    segment_length: int = 500,
    data_dir: str = "data",
) -> List[RoadSegment]:
    """Quick function to extract roads and show a plot.

    Args:
        country: Country name
        region: Region name
        n: Number of segments to sample (None = plot all)
        admin_level: Administrative level
        road_types: Road types to include
        segment_length: Target segment length in meters
        data_dir: Directory for caching downloaded data

    Returns:
        List of RoadSegment objects that were plotted
    """
    extractor = RoadExtractor(country, region, admin_level, data_dir)
    all_roads = extractor.get_roads(road_types, segment_length)

    if n is None:
        # Plot all roads
        extractor.plot(road_types, segment_length)
        return all_roads
    else:
        # Sample and plot
        sampler = RoadSampler(all_roads)
        sample = sampler.random_sample(n)
        sampler.plot_sample(sample)
        return sample


def get_road_summary(
    country: str, region: str, admin_level: int = 1, data_dir: str = "data"
) -> dict:
    """Get summary statistics for roads in a region.

    Args:
        country: Country name
        region: Region name
        admin_level: Administrative level
        data_dir: Directory for caching downloaded data

    Returns:
        Dictionary with summary statistics
    """
    extractor = RoadExtractor(country, region, admin_level, data_dir)
    all_roads = extractor.get_roads()

    sampler = RoadSampler(all_roads)
    road_type_counts = sampler.get_road_type_summary()

    return {
        "total_segments": len(all_roads),
        "road_types": list(road_type_counts.keys()),
        "road_type_counts": road_type_counts,
        "region": f"{region}, {country}",
        "admin_level": admin_level,
    }
