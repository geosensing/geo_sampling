"""
Utility functions for the geo_sampling package.

This module provides functions for plotting road segments and writing CSV files.
"""

import csv
import matplotlib.pyplot as plt
from matplotlib import colors


def plot_road_segments(segments, title="Road Segments Plot"):
    """
    Plot multiple road segments with different colors based on road type.

    Args:
        segments (list of dict): List of road segment dictionaries. Each dictionary
            should contain:
                - 'start_lat' (float): Latitude of the starting point.
                - 'start_long' (float): Longitude of the starting point.
                - 'end_lat' (float): Latitude of the ending point.
                - 'end_long' (float): Longitude of the ending point.
                - 'osm_type' (str): Road type.
        title (str): Title for the plot.

    Returns:
        None. Displays the plot.
    """
    _, axis = plt.subplots(figsize=(12, 10))
    color_values = list(colors.cnames.values())
    road_color_map = {}  # Maps road type to color

    for segment in segments:
        x_coords = [segment["start_long"], segment["end_long"]]
        y_coords = [segment["start_lat"], segment["end_lat"]]
        road_type = segment["osm_type"]

        if road_type not in road_color_map:
            road_color_map[road_type] = color_values[len(road_color_map) % len(color_values)]

        # Get current legend labels
        _, current_labels = axis.get_legend_handles_labels()
        label = road_type if road_type not in current_labels else ""
        axis.plot(x_coords, y_coords, color=road_color_map[road_type],
                  linewidth=1.2, label=label)

    # Format the axes for better display
    axis.get_yaxis().get_major_formatter().set_useOffset(False)
    axis.get_yaxis().get_major_formatter().set_scientific(False)
    axis.get_xaxis().get_major_formatter().set_useOffset(False)
    axis.get_xaxis().get_major_formatter().set_scientific(False)
    plt.title(title)
    plt.legend(loc="best", fancybox=True, framealpha=0.5)
    plt.grid(True)
    plt.show()


def write_csv(file_path, data, no_header=False):
    """
    Write a list of dictionaries to a CSV file.

    Args:
        file_path (str): The output CSV file path.
        data (list of dict): The data to be written.
        no_header (bool): If True, the CSV header will not be written.

    Returns:
        None.
    """
    columns = [
        "segment_id", "osm_id", "osm_name", "osm_type", 
        "start_lat", "start_long", "end_lat", "end_long"
    ]
    with open(file_path, "w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(out_file, fieldnames=columns)
        if not no_header:
            writer.writeheader()
        writer.writerows(data)
