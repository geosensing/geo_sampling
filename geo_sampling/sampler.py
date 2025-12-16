"""Road sampling functionality."""

import csv
import random
from collections import defaultdict
from typing import List, Optional, Union, Dict
from pathlib import Path

from ._types import RoadSegment, RoadTypeFilter
from .visualization import RoadPlotter


class RoadSampler:
    """Class for sampling road segments with various strategies."""

    def __init__(self, segments: List[RoadSegment]):
        """Initialize sampler with road segments.

        Args:
            segments: List of road segments to sample from
        """
        self.segments = segments
        self._validate_segments()

    def random_sample(
        self, n: int, road_types: RoadTypeFilter = None, seed: Optional[int] = None
    ) -> List[RoadSegment]:
        """Get random sample of road segments.

        Args:
            n: Number of segments to sample
            road_types: Road types to include (None = all types)
            seed: Random seed for reproducibility

        Returns:
            List of sampled RoadSegment objects

        Raises:
            ValueError: If sample size exceeds available segments
        """
        if seed is not None:
            random.seed(seed)

        # Filter by road types if specified
        available_segments = self._filter_by_road_types(road_types)

        if n > len(available_segments):
            raise ValueError(
                f"Sample size {n} exceeds available segments {len(available_segments)}"
            )

        if n <= 0:
            return []

        return random.sample(available_segments, n)

    def stratified_sample(
        self,
        n: int,
        by: str = "osm_type",
        road_types: RoadTypeFilter = None,
        seed: Optional[int] = None,
    ) -> List[RoadSegment]:
        """Get stratified sample maintaining proportions across strata.

        Args:
            n: Total number of segments to sample
            by: Field to stratify by (default: "osm_type")
            road_types: Road types to include
            seed: Random seed for reproducibility

        Returns:
            List of sampled RoadSegment objects
        """
        if seed is not None:
            random.seed(seed)

        available_segments = self._filter_by_road_types(road_types)

        if n > len(available_segments):
            raise ValueError(
                f"Sample size {n} exceeds available segments {len(available_segments)}"
            )

        # Group segments by stratification field
        strata = defaultdict(list)
        for segment in available_segments:
            stratum_value = getattr(segment, by)
            strata[stratum_value].append(segment)

        # Calculate sample sizes for each stratum
        total_segments = len(available_segments)
        sampled_segments = []

        # Proportional allocation
        allocated = 0
        stratum_samples = {}

        for stratum, stratum_segments in strata.items():
            proportion = len(stratum_segments) / total_segments
            stratum_n = int(round(n * proportion))

            # Ensure we don't exceed available segments in this stratum
            stratum_n = min(stratum_n, len(stratum_segments))
            stratum_samples[stratum] = stratum_n
            allocated += stratum_n

        # Adjust for rounding errors - add remaining to largest strata
        remaining = n - allocated
        if remaining > 0:
            # Sort strata by size and allocate remaining samples
            sorted_strata = sorted(
                strata.items(), key=lambda x: len(x[1]), reverse=True
            )

            for stratum, stratum_segments in sorted_strata:
                if remaining <= 0:
                    break

                # Add one more if possible
                current_allocation = stratum_samples[stratum]
                if current_allocation < len(stratum_segments):
                    stratum_samples[stratum] += 1
                    remaining -= 1

        # Sample from each stratum
        for stratum, stratum_segments in strata.items():
            stratum_n = stratum_samples[stratum]
            if stratum_n > 0:
                stratum_sample = random.sample(stratum_segments, stratum_n)
                sampled_segments.extend(stratum_sample)

        # Shuffle final results
        random.shuffle(sampled_segments)
        return sampled_segments

    def sample_by_length(
        self,
        target_length_km: float,
        road_types: RoadTypeFilter = None,
        seed: Optional[int] = None,
    ) -> List[RoadSegment]:
        """Sample segments to approximate a target total length.

        Args:
            target_length_km: Target total length in kilometers
            road_types: Road types to include
            seed: Random seed for reproducibility

        Returns:
            List of sampled RoadSegment objects
        """
        if seed is not None:
            random.seed(seed)

        available_segments = self._filter_by_road_types(road_types)

        # Calculate segment lengths (assuming 500m segments)
        # In a real implementation, you'd calculate actual lengths
        segment_length_km = 0.5  # 500m = 0.5km

        target_n = int(target_length_km / segment_length_km)

        if target_n > len(available_segments):
            print(
                f"Warning: Target length requires {target_n} segments, "
                f"but only {len(available_segments)} available. Using all."
            )
            return available_segments

        return random.sample(available_segments, target_n)

    def get_road_type_summary(
        self, road_types: RoadTypeFilter = None
    ) -> Dict[str, int]:
        """Get count summary by road type.

        Args:
            road_types: Road types to include

        Returns:
            Dictionary mapping road type to count
        """
        segments = self._filter_by_road_types(road_types)

        summary = defaultdict(int)
        for segment in segments:
            summary[segment.osm_type] += 1

        return dict(summary)

    def save_csv(self, segments: List[RoadSegment], path: Union[str, Path]) -> None:
        """Save segments to CSV file.

        Args:
            segments: Road segments to save
            path: Output file path
        """
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

    def plot_sample(
        self,
        sample: List[RoadSegment],
        title: Optional[str] = None,
        show_comparison: bool = True,
        figsize: tuple = (12, 10),
    ) -> None:
        """Plot sampled segments.

        Args:
            sample: Sampled road segments
            title: Plot title
            show_comparison: Whether to show comparison with full dataset
            figsize: Figure size
        """
        plotter = RoadPlotter(figsize=figsize)

        if show_comparison and len(self.segments) > len(sample):
            plotter.plot_sample_comparison(self.segments, sample)
        else:
            if not title:
                title = f"Road Segments Sample (N = {len(sample)})"
            plotter.plot(sample, title=title)

    def to_dataframe(self, segments: List[RoadSegment]):
        """Convert segments to pandas DataFrame.

        Args:
            segments: Road segments to convert

        Returns:
            pandas.DataFrame with segment data
        """
        import pandas as pd

        data = [segment.to_dict() for segment in segments]
        return pd.DataFrame(data)

    def _filter_by_road_types(self, road_types: RoadTypeFilter) -> List[RoadSegment]:
        """Filter segments by road types."""
        if not road_types:
            return self.segments

        # Convert single string to list
        if isinstance(road_types, str):
            road_types = [road_types]

        return [seg for seg in self.segments if seg.osm_type in road_types]

    def _validate_segments(self) -> None:
        """Validate input segments."""
        if not self.segments:
            raise ValueError("No segments provided for sampling")

        if not all(isinstance(seg, RoadSegment) for seg in self.segments):
            raise ValueError("All segments must be RoadSegment objects")


def load_segments_from_csv(path: Union[str, Path]) -> List[RoadSegment]:
    """Load road segments from CSV file.

    Args:
        path: Path to CSV file

    Returns:
        List of RoadSegment objects
    """
    segments = []

    with open(path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(RoadSegment.from_dict(row))

    return segments


def sample_roads(
    segments: List[RoadSegment],
    n: int,
    road_types: RoadTypeFilter = None,
    strategy: str = "random",
    seed: Optional[int] = None,
) -> List[RoadSegment]:
    """Convenience function to sample roads.

    Args:
        segments: Road segments to sample from
        n: Number of segments to sample
        road_types: Road types to include
        strategy: Sampling strategy ("random" or "stratified")
        seed: Random seed

    Returns:
        List of sampled RoadSegment objects
    """
    sampler = RoadSampler(segments)

    if strategy == "random":
        return sampler.random_sample(n, road_types, seed)
    elif strategy == "stratified":
        return sampler.stratified_sample(n, road_types=road_types, seed=seed)
    else:
        raise ValueError(f"Unknown sampling strategy: {strategy}")
