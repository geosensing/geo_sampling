"""Visualization utilities for road segments."""

from typing import List, Dict
import matplotlib.pyplot as plt
from matplotlib import colors

from ._types import RoadSegment


class RoadPlotter:
    """Handles plotting of road segments with automatic styling."""

    def __init__(self, figsize: tuple = (12, 10)):
        """Initialize plotter.

        Args:
            figsize: Figure size for plots
        """
        self.figsize = figsize
        self.color_map: Dict[str, str] = {}
        self._color_values = list(colors.CSS4_COLORS.keys())
        self._color_index = 0

    def plot(
        self,
        segments: List[RoadSegment],
        title: str = "Road Segments",
        show_legend: bool = True,
        grid: bool = True,
    ) -> None:
        """Plot road segments with different colors by road type.

        Args:
            segments: List of road segments to plot
            title: Plot title
            show_legend: Whether to show legend
            grid: Whether to show grid
        """
        if not segments:
            print("No segments to plot")
            return

        fig, ax = plt.subplots(figsize=self.figsize)

        # Track which road types we've already added to legend
        legend_labels = set()

        for segment in segments:
            x_coords = [segment.start_long, segment.end_long]
            y_coords = [segment.start_lat, segment.end_lat]

            # Get color for this road type
            color = self._get_road_color(segment.osm_type)

            # Only add label if this road type hasn't been added yet
            label = segment.osm_type if segment.osm_type not in legend_labels else ""
            if label:
                legend_labels.add(segment.osm_type)

            ax.plot(
                x_coords, y_coords, color=color, linewidth=1.2, label=label, alpha=0.8
            )

        # Format axes
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title(title)

        if show_legend and legend_labels:
            ax.legend(loc="best", fancybox=True, framealpha=0.7)

        if grid:
            ax.grid(True, alpha=0.3)

        plt.tight_layout()
        plt.show()

    def plot_sample_comparison(
        self, all_segments: List[RoadSegment], sampled_segments: List[RoadSegment]
    ) -> None:
        """Plot comparison between all segments and sample.

        Args:
            all_segments: Complete set of road segments
            sampled_segments: Sampled subset
        """
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(20, 8))

        # Plot all segments
        self._plot_on_axis(ax1, all_segments, f"All Segments (N = {len(all_segments)})")

        # Plot sampled segments
        self._plot_on_axis(
            ax2, sampled_segments, f"Sample (N = {len(sampled_segments)})"
        )

        plt.tight_layout()
        plt.show()

    def _plot_on_axis(self, ax, segments: List[RoadSegment], title: str) -> None:
        """Plot segments on a specific axis."""
        legend_labels = set()

        for segment in segments:
            x_coords = [segment.start_long, segment.end_long]
            y_coords = [segment.start_lat, segment.end_lat]

            color = self._get_road_color(segment.osm_type)
            label = segment.osm_type if segment.osm_type not in legend_labels else ""
            if label:
                legend_labels.add(segment.osm_type)

            ax.plot(
                x_coords, y_coords, color=color, linewidth=1.2, label=label, alpha=0.8
            )

        # Format axis
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)

        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        if legend_labels:
            ax.legend(loc="best", fancybox=True, framealpha=0.7)

    def _get_road_color(self, road_type: str) -> str:
        """Get consistent color for a road type."""
        if road_type not in self.color_map:
            # Assign next color
            self.color_map[road_type] = self._color_values[
                self._color_index % len(self._color_values)
            ]
            self._color_index += 1

        return self.color_map[road_type]


def plot_road_segments(
    segments: List[RoadSegment],
    title: str = "Road Segments",
    figsize: tuple = (12, 10),
    show_legend: bool = True,
) -> None:
    """Convenience function to plot road segments.

    Args:
        segments: List of road segments to plot
        title: Plot title
        figsize: Figure size
        show_legend: Whether to show legend
    """
    plotter = RoadPlotter(figsize=figsize)
    plotter.plot(segments, title=title, show_legend=show_legend)
