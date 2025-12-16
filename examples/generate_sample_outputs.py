#!/usr/bin/env python3
"""Generate sample outputs for documentation and testing.

This script creates representative sample data that demonstrates the package
functionality without requiring network access or real OSM data downloads.
"""

import os
import random
import geo_sampling as gs
import matplotlib.pyplot as plt
from geo_sampling._types import RoadSegment


def create_delhi_like_data():
    """Create sample data that resembles Delhi road network."""
    # Delhi-like coordinates (NCT of Delhi bounds approximately)
    delhi_bounds = {
        "lat_min": 28.4,
        "lat_max": 28.9,
        "long_min": 76.8,
        "long_max": 77.3,
    }

    segments = []
    segment_id = 1

    # Generate different types of roads with realistic distributions
    road_types = [
        ("trunk", 50, "NH-1", "NH-8"),  # National Highways
        ("primary", 120, "Ring Road", "GT Road", "Outer Ring Road"),  # Major roads
        (
            "secondary",
            200,
            "MG Road",
            "CP Road",
            "Lajpat Nagar Road",
        ),  # Secondary roads
        ("tertiary", 300, "Local Road", "Sector Road", "Block Road"),  # Tertiary roads
        ("residential", 400, "Street", "Lane", "Gali"),  # Residential streets
        ("unclassified", 150, "Service Road", "Access Road"),  # Service roads
    ]

    random.seed(42)  # For reproducibility

    for road_type, count, *name_prefixes in road_types:
        for i in range(count):
            # Generate realistic coordinates within Delhi bounds
            start_lat = random.uniform(delhi_bounds["lat_min"], delhi_bounds["lat_max"])
            start_long = random.uniform(
                delhi_bounds["long_min"], delhi_bounds["long_max"]
            )

            # Generate end point ~500m away (rough approximation)
            lat_offset = random.uniform(-0.005, 0.005)  # ~500m in latitude
            long_offset = random.uniform(-0.005, 0.005)  # ~500m in longitude

            end_lat = start_lat + lat_offset
            end_long = start_long + long_offset

            # Keep within bounds
            end_lat = max(
                delhi_bounds["lat_min"], min(delhi_bounds["lat_max"], end_lat)
            )
            end_long = max(
                delhi_bounds["long_min"], min(delhi_bounds["long_max"], end_long)
            )

            # Generate realistic road name
            name_prefix = random.choice(name_prefixes)
            road_name = (
                f"{name_prefix} {i + 1}" if len(name_prefixes) > 1 else f"{name_prefix}"
            )

            segment = RoadSegment(
                segment_id=segment_id,
                osm_id=f"way_{segment_id}",
                osm_name=road_name,
                osm_type=road_type,
                start_lat=start_lat,
                start_long=start_long,
                end_lat=end_lat,
                end_long=end_long,
            )

            segments.append(segment)
            segment_id += 1

    return segments


def create_singapore_like_data():
    """Create sample data that resembles Singapore road network."""
    # Singapore Central region bounds
    singapore_bounds = {
        "lat_min": 1.25,
        "lat_max": 1.35,
        "long_min": 103.80,
        "long_max": 103.90,
    }

    segments = []
    segment_id = 1

    # Singapore road type distribution
    road_types = [
        ("trunk", 20, "PIE", "CTE", "AYE"),  # Expressways
        ("primary", 40, "Orchard Road", "Marina Bay", "Raffles Place"),  # Major roads
        ("secondary", 80, "Toa Payoh Road", "Clementi Road"),  # Secondary roads
        ("tertiary", 120, "Serangoon Road", "East Coast Road"),  # Tertiary roads
        ("residential", 150, "HDB Estate Road", "Condo Access"),  # Residential
        ("unclassified", 60, "Service Road"),  # Service roads
    ]

    random.seed(123)  # Different seed for Singapore

    for road_type, count, *name_prefixes in road_types:
        for i in range(count):
            start_lat = random.uniform(
                singapore_bounds["lat_min"], singapore_bounds["lat_max"]
            )
            start_long = random.uniform(
                singapore_bounds["long_min"], singapore_bounds["long_max"]
            )

            # Smaller road segments for dense Singapore
            lat_offset = random.uniform(-0.003, 0.003)  # ~300m segments
            long_offset = random.uniform(-0.003, 0.003)

            end_lat = start_lat + lat_offset
            end_long = start_long + long_offset

            # Keep within bounds
            end_lat = max(
                singapore_bounds["lat_min"], min(singapore_bounds["lat_max"], end_lat)
            )
            end_long = max(
                singapore_bounds["long_min"],
                min(singapore_bounds["long_max"], end_long),
            )

            name_prefix = random.choice(name_prefixes)
            road_name = (
                f"{name_prefix} {i + 1}" if len(name_prefixes) > 1 else f"{name_prefix}"
            )

            segment = RoadSegment(
                segment_id=segment_id,
                osm_id=f"sg_way_{segment_id}",
                osm_name=road_name,
                osm_type=road_type,
                start_lat=start_lat,
                start_long=start_long,
                end_lat=end_lat,
                end_long=end_long,
            )

            segments.append(segment)
            segment_id += 1

    return segments


def generate_basic_workflow_outputs():
    """Generate outputs for the basic workflow example."""
    print("Generating Delhi-like sample data for basic workflow...")

    output_dir = "examples/outputs/01_basic_workflow"
    os.makedirs(output_dir, exist_ok=True)

    # Create Delhi-like road data
    all_roads = create_delhi_like_data()
    print(f"Created {len(all_roads)} road segments")

    # Save all roads
    sampler = gs.RoadSampler(all_roads)
    all_roads_file = os.path.join(output_dir, "delhi_all_roads.csv")
    sampler.save_csv(all_roads, all_roads_file)
    print(f"Saved all roads to {all_roads_file}")

    # Create sample
    sample_roads = sampler.random_sample(1000, seed=42)
    sample_file = os.path.join(output_dir, "delhi_sampled_roads.csv")
    sampler.save_csv(sample_roads, sample_file)
    print(f"Saved sample to {sample_file}")

    # Create visualizations
    plt.ioff()

    # Sample plot
    plt.figure(figsize=(12, 8))
    gs.plot_road_segments(
        sample_roads, title=f"Delhi Road Sample (N={len(sample_roads)})"
    )
    sample_plot_file = os.path.join(output_dir, "delhi_sample_plot.png")
    plt.savefig(sample_plot_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved sample plot to {sample_plot_file}")

    # Comparison plot
    if len(all_roads) < 5000:  # Only if manageable
        plotter = gs.RoadPlotter(figsize=(16, 8))
        plotter.plot_sample_comparison(all_roads, sample_roads)
        comparison_plot_file = os.path.join(output_dir, "delhi_comparison_plot.png")
        plt.savefig(comparison_plot_file, dpi=150, bbox_inches="tight")
        plt.close()
        print(f"Saved comparison plot to {comparison_plot_file}")

    return all_roads, sample_roads


def generate_advanced_sampling_outputs():
    """Generate outputs for the advanced sampling example."""
    print("\nGenerating Singapore-like sample data for advanced sampling...")

    output_dir = "examples/outputs/02_advanced_sampling"
    os.makedirs(output_dir, exist_ok=True)

    # Create Singapore-like road data
    all_roads = create_singapore_like_data()
    print(f"Created {len(all_roads)} road segments")

    sampler = gs.RoadSampler(all_roads)

    # Save all roads data
    all_roads_file = os.path.join(output_dir, "singapore_all_roads.csv")
    sampler.save_csv(all_roads, all_roads_file)

    # Generate different sampling strategies
    random.seed(42)

    # Random sample
    random_sample = sampler.random_sample(200, seed=42)
    random_file = os.path.join(output_dir, "singapore_random_sample.csv")
    sampler.save_csv(random_sample, random_file)
    print(f"Saved random sample ({len(random_sample)}) to {random_file}")

    # Stratified sample
    stratified_sample = sampler.stratified_sample(150, seed=42)
    stratified_file = os.path.join(output_dir, "singapore_stratified_sample.csv")
    sampler.save_csv(stratified_sample, stratified_file)
    print(f"Saved stratified sample ({len(stratified_sample)}) to {stratified_file}")

    # Filtered sample (major roads only)
    major_road_types = ["trunk", "primary", "secondary"]
    filtered_sample = sampler.random_sample(100, road_types=major_road_types, seed=42)
    filtered_file = os.path.join(output_dir, "singapore_filtered_sample.csv")
    sampler.save_csv(filtered_sample, filtered_file)
    print(f"Saved filtered sample ({len(filtered_sample)}) to {filtered_file}")

    # Create comparison visualization
    plt.ioff()
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))

    # Plot all roads (subset for visibility)
    all_subset = random.sample(all_roads, min(300, len(all_roads)))
    plot_segments_on_axis(axes[0], all_subset, f"All Roads (N={len(all_roads)})")

    # Plot random sample
    plot_segments_on_axis(
        axes[1], random_sample, f"Random Sample (N={len(random_sample)})"
    )

    # Plot stratified sample
    plot_segments_on_axis(
        axes[2], stratified_sample, f"Stratified Sample (N={len(stratified_sample)})"
    )

    plt.tight_layout()
    comparison_plot_file = os.path.join(output_dir, "singapore_comparison_plots.png")
    plt.savefig(comparison_plot_file, dpi=150, bbox_inches="tight")
    plt.close()
    print(f"Saved comparison plots to {comparison_plot_file}")

    return all_roads, random_sample, stratified_sample, filtered_sample


def plot_segments_on_axis(ax, segments, title):
    """Plot segments on a specific axis with road type coloring."""
    if not segments:
        ax.set_title(title + " (No data)")
        return

    # Group by road type for consistent coloring
    road_types = {}
    for segment in segments:
        if segment.osm_type not in road_types:
            road_types[segment.osm_type] = []
        road_types[segment.osm_type].append(segment)

    # Color map for road types
    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink", "gray"]

    for i, (road_type, type_segments) in enumerate(road_types.items()):
        color = colors[i % len(colors)]

        for segment in type_segments:
            x_coords = [segment.start_long, segment.end_long]
            y_coords = [segment.start_lat, segment.end_lat]
            ax.plot(x_coords, y_coords, color=color, linewidth=1.0, alpha=0.7)

    # Format axis
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")
    ax.set_title(title)
    ax.grid(True, alpha=0.3)

    # Create legend
    legend_elements = [
        plt.Line2D([0], [0], color=colors[i % len(colors)], label=road_type)
        for i, road_type in enumerate(road_types.keys())
    ]
    if (
        legend_elements and len(legend_elements) <= 6
    ):  # Only show legend if not too many types
        ax.legend(handles=legend_elements, loc="best", fontsize="small")


def generate_cli_demonstration_output():
    """Generate output showing CLI command examples."""
    print("\nGenerating CLI demonstration outputs...")

    output_dir = "examples/outputs/03_cli_usage"
    os.makedirs(output_dir, exist_ok=True)

    # Create a commands log file
    commands_log = os.path.join(output_dir, "commands_log.txt")

    with open(commands_log, "w") as f:
        f.write("GEO-SAMPLING CLI COMMANDS DEMONSTRATION\\n")
        f.write("=====================================\\n\\n")

        f.write("# Extract roads from Delhi\\n")
        f.write(
            'geo-sampling extract "India" "NCT of Delhi" --output delhi_roads.csv\\n\\n'
        )

        f.write("# Sample 1000 random segments\\n")
        f.write(
            "geo-sampling sample delhi_roads.csv --sample-size 1000 --output delhi_sample.csv\\n\\n"
        )

        f.write("# Complete workflow for Singapore\\n")
        f.write(
            'geo-sampling workflow "Singapore" "Central" --sample-size 100 --output singapore_sample.csv\\n\\n'
        )

        f.write("# Get region information\\n")
        f.write('geo-sampling info "Thailand" "Bangkok"\\n\\n')

        f.write("# Advanced sampling with filtering\\n")
        f.write(
            "geo-sampling sample roads.csv --sample-size 500 --road-types primary --road-types secondary --strategy stratified\\n\\n"
        )

    print(f"Created CLI commands log: {commands_log}")

    # Create some sample output files in the sample_outputs directory
    sample_outputs_dir = os.path.join(output_dir, "sample_outputs")
    os.makedirs(sample_outputs_dir, exist_ok=True)

    # Create a small sample dataset to demonstrate CLI usage
    test_segments = create_singapore_like_data()[:50]  # Small subset
    test_sampler = gs.RoadSampler(test_segments)

    # Save as if created by CLI
    cli_output_file = os.path.join(sample_outputs_dir, "cli_extracted_roads.csv")
    test_sampler.save_csv(test_segments, cli_output_file)

    # Create sample
    cli_sample = test_sampler.random_sample(20, seed=42)
    cli_sample_file = os.path.join(sample_outputs_dir, "cli_sample.csv")
    test_sampler.save_csv(cli_sample, cli_sample_file)

    print(f"Created sample CLI outputs in {sample_outputs_dir}")


def main():
    """Generate all sample outputs."""
    print("Generating sample outputs for geo_sampling examples...")
    print("=" * 60)

    # Generate outputs for each example
    delhi_all, delhi_sample = generate_basic_workflow_outputs()
    singapore_all, sg_random, sg_stratified, sg_filtered = (
        generate_advanced_sampling_outputs()
    )
    generate_cli_demonstration_output()

    print("\\n" + "=" * 60)
    print("SAMPLE OUTPUTS GENERATION COMPLETE")
    print("=" * 60)
    print()
    print("Generated outputs:")
    print("- examples/outputs/01_basic_workflow/")
    print("  - delhi_all_roads.csv (1,220 segments)")
    print("  - delhi_sampled_roads.csv (1,000 segments)")
    print("  - delhi_sample_plot.png")
    print("  - delhi_comparison_plot.png")
    print()
    print("- examples/outputs/02_advanced_sampling/")
    print("  - singapore_all_roads.csv (470 segments)")
    print("  - singapore_random_sample.csv (200 segments)")
    print("  - singapore_stratified_sample.csv (150 segments)")
    print("  - singapore_filtered_sample.csv (100 segments)")
    print("  - singapore_comparison_plots.png")
    print()
    print("- examples/outputs/03_cli_usage/")
    print("  - commands_log.txt")
    print("  - sample_outputs/cli_extracted_roads.csv")
    print("  - sample_outputs/cli_sample.csv")
    print()
    print("All outputs are ready for distribution!")


if __name__ == "__main__":
    main()
