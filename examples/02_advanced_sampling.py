#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Advanced Sampling Strategies Example

This example demonstrates different sampling strategies available in the
geo_sampling package, including:

1. Random sampling with road type filtering
2. Stratified sampling to maintain proportions
3. Length-based sampling for specific coverage
4. Statistical analysis of sampling results
5. Comparative visualizations
6. CLI command equivalents

Uses Singapore as the test region for faster execution.

NETWORK REQUIRED: This example requires an active internet connection to download
geographic data from BBBike.org and GADM. The example will fail if the network
is unavailable.

OUTPUT: Results are saved to examples/outputs/02_advanced_sampling/
"""

import os
import time
import geo_sampling as gs
import matplotlib.pyplot as plt


def show_cli_equivalents():
    """Show CLI commands equivalent to the Python sampling strategies."""
    print("\n" + "=" * 60)
    print("CLI EQUIVALENTS FOR ADVANCED SAMPLING")
    print("=" * 60)

    print("1. RANDOM SAMPLING:")
    print("geo-sampling sample singapore_all_roads.csv \\")
    print("    --sample-size 200 \\")
    print("    --strategy random \\")
    print("    --seed 42 \\")
    print("    --output singapore_random_sample.csv")
    print()

    print("2. STRATIFIED SAMPLING:")
    print("geo-sampling sample singapore_all_roads.csv \\")
    print("    --sample-size 150 \\")
    print("    --strategy stratified \\")
    print("    --seed 42 \\")
    print("    --output singapore_stratified_sample.csv")
    print()

    print("3. ROAD TYPE FILTERING:")
    print("geo-sampling sample singapore_all_roads.csv \\")
    print("    --sample-size 100 \\")
    print("    --road-types primary secondary \\")
    print("    --output singapore_filtered_sample.csv")
    print()

    print("4. COMPLETE WORKFLOW WITH FILTERING:")
    print('geo-sampling workflow "Singapore" "Central" \\')
    print("    --sample-size 100 \\")
    print("    --road-types primary secondary tertiary \\")
    print("    --strategy stratified \\")
    print("    --plot \\")
    print("    --output singapore_advanced_sample.csv")
    print()


def main():
    """Execute advanced sampling strategies example."""
    print("=" * 60)
    print("Advanced Sampling Strategies: Singapore")
    print("=" * 60)

    # Configuration - using smaller region for faster execution
    country = "Singapore"
    region = "Central"  # Singapore administrative region
    admin_level = 1

    # Create output directory structure
    output_dir = "examples/outputs/02_advanced_sampling"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Region: {region}, {country}")
    print()

    # Step 1: Extract road data
    print("Step 1: Extracting road segments...")
    start_time = time.time()

    try:
        extractor = gs.RoadExtractor(country, region, admin_level)
        all_roads = extractor.get_roads()
        extraction_time = time.time() - start_time

        print(f"✓ Extracted {len(all_roads)} road segments in {extraction_time:.1f}s")

        # Analyze road types
        sampler = gs.RoadSampler(all_roads)
        road_summary = sampler.get_road_type_summary()
        print(f"Road type distribution: {dict(road_summary)}")
        print()

    except Exception as e:
        print(f"✗ Failed to extract roads: {e}")
        print("Check your internet connection and try again.")
        return

    # Step 2: Demonstrate different sampling strategies
    demonstrate_random_sampling(sampler, all_roads, output_dir)
    demonstrate_stratified_sampling(sampler, output_dir)
    demonstrate_road_type_filtering(sampler, output_dir)
    demonstrate_length_based_sampling(sampler, output_dir)

    # Step 3: Comparative analysis
    comparative_analysis(sampler, all_roads, output_dir)

    print("\nAdvanced sampling example completed!")
    print(f"Check outputs in: {output_dir}")


def demonstrate_random_sampling(sampler, all_roads, output_dir):
    """Demonstrate random sampling with different parameters."""
    print("=" * 50)
    print("Random Sampling Strategies")
    print("=" * 50)

    # Basic random sampling
    sample_size = min(200, len(all_roads) // 4)
    random_sample = sampler.random_sample(sample_size, seed=42)

    print(f"Random sample (n={sample_size}):")
    sample_types = gs.RoadSampler(random_sample).get_road_type_summary()
    print(f"  Types: {dict(sample_types)}")

    # Reproducibility test
    random_sample2 = sampler.random_sample(sample_size, seed=42)
    if random_sample == random_sample2:
        print("  ✓ Reproducible with seed=42")
    else:
        print("  ✗ Not reproducible - check implementation")

    # Different seed
    random_sample3 = sampler.random_sample(sample_size, seed=123)
    if random_sample != random_sample3:
        print("  ✓ Different results with different seed")

    # Save random sample
    random_sample_file = os.path.join(output_dir, "singapore_random_sample.csv")
    sampler.save_csv(random_sample, random_sample_file)
    print(f"  ✓ Saved random sample to: {random_sample_file}")

    print()


def demonstrate_stratified_sampling(sampler, output_dir):
    """Demonstrate stratified sampling to maintain proportions."""
    print("=" * 50)
    print("Stratified Sampling")
    print("=" * 50)

    sample_size = min(150, len(sampler.segments) // 3)

    # Get original proportions
    original_summary = sampler.get_road_type_summary()
    total_roads = sum(original_summary.values())

    print("Original proportions:")
    for road_type, count in original_summary.items():
        proportion = count / total_roads * 100
        print(f"  {road_type}: {count} ({proportion:.1f}%)")

    # Stratified sampling
    stratified_sample = sampler.stratified_sample(sample_size, seed=42)
    stratified_summary = gs.RoadSampler(stratified_sample).get_road_type_summary()

    print(f"\nStratified sample (n={sample_size}) proportions:")
    for road_type, count in stratified_summary.items():
        proportion = count / len(stratified_sample) * 100
        original_prop = original_summary.get(road_type, 0) / total_roads * 100
        print(
            f"  {road_type}: {count} ({proportion:.1f}% vs {original_prop:.1f}% original)"
        )

    # Save stratified sample
    stratified_sample_file = os.path.join(output_dir, "singapore_stratified_sample.csv")
    sampler.save_csv(stratified_sample, stratified_sample_file)
    print(f"✓ Saved stratified sample to: {stratified_sample_file}")

    print()


def demonstrate_road_type_filtering(sampler, output_dir):
    """Demonstrate filtering by road types."""
    print("=" * 50)
    print("Road Type Filtering")
    print("=" * 50)

    road_summary = sampler.get_road_type_summary()
    available_types = list(road_summary.keys())

    if len(available_types) < 2:
        print("Not enough road types for filtering demo")
        return

    # Single road type filtering
    primary_type = available_types[0]
    single_type_sample = sampler.random_sample(50, road_types=[primary_type], seed=42)

    print(f"Single type filter ({primary_type}):")
    print(f"  Sample size: {len(single_type_sample)}")
    print(
        f"  All segments are '{primary_type}': {all(s.osm_type == primary_type for s in single_type_sample)}"
    )

    # Multiple road type filtering
    if len(available_types) >= 2:
        filtered_types = available_types[:2]
        multi_type_sample = sampler.random_sample(
            100, road_types=filtered_types, seed=42
        )

        print(f"\nMultiple type filter {filtered_types}:")
        print(f"  Sample size: {len(multi_type_sample)}")

        multi_summary = gs.RoadSampler(multi_type_sample).get_road_type_summary()
        print(f"  Types in sample: {list(multi_summary.keys())}")

        # Save filtered sample
        filtered_sample_file = os.path.join(output_dir, "singapore_filtered_sample.csv")
        sampler.save_csv(multi_type_sample, filtered_sample_file)
        print(f"  ✓ Saved filtered sample to: {filtered_sample_file}")

    print()


def demonstrate_length_based_sampling(sampler, output_dir):
    """Demonstrate sampling by target length coverage."""
    print("=" * 50)
    print("Length-Based Sampling")
    print("=" * 50)

    # Assuming each segment is ~0.5km (500m default split)
    target_lengths = [1.0, 2.5, 5.0]  # kilometers

    for target_km in target_lengths:
        length_sample = sampler.sample_by_length(target_km, seed=42)
        actual_km = len(length_sample) * 0.5  # Approximate

        print(
            f"Target: {target_km}km → Sample: {len(length_sample)} segments (~{actual_km}km)"
        )

    print()


def comparative_analysis(sampler, all_roads, output_dir):
    """Compare different sampling strategies visually and statistically."""
    print("=" * 50)
    print("Comparative Analysis")
    print("=" * 50)

    sample_size = min(100, len(all_roads) // 5)

    # Generate different samples
    random_sample = sampler.random_sample(sample_size, seed=42)
    stratified_sample = sampler.stratified_sample(sample_size, seed=42)

    # Statistical comparison
    print(f"Sample size: {sample_size}")
    print("\nRoad type distributions:")

    original_summary = sampler.get_road_type_summary()
    random_summary = gs.RoadSampler(random_sample).get_road_type_summary()
    stratified_summary = gs.RoadSampler(stratified_sample).get_road_type_summary()

    total_original = sum(original_summary.values())

    print(f"{'Type':<12} {'Original':<10} {'Random':<10} {'Stratified':<10}")
    print("-" * 50)

    for road_type in original_summary.keys():
        orig_pct = original_summary[road_type] / total_original * 100
        rand_pct = random_summary.get(road_type, 0) / sample_size * 100
        strat_pct = stratified_summary.get(road_type, 0) / sample_size * 100

        print(
            f"{road_type:<12} {orig_pct:>7.1f}%   {rand_pct:>7.1f}%   {strat_pct:>7.1f}%"
        )

    # Visualizations
    print("\nCreating comparative visualizations...")

    try:
        # Create subplot comparison
        fig, axes = plt.subplots(1, 3, figsize=(18, 6))

        # Plot all roads
        plot_segments_on_axis(axes[0], all_roads, f"All Roads (N={len(all_roads)})")

        # Plot random sample
        plot_segments_on_axis(
            axes[1], random_sample, f"Random Sample (N={len(random_sample)})"
        )

        # Plot stratified sample
        plot_segments_on_axis(
            axes[2],
            stratified_sample,
            f"Stratified Sample (N={len(stratified_sample)})",
        )

        plt.tight_layout()
        comparison_plot_file = os.path.join(
            output_dir, "singapore_comparison_plots.png"
        )
        plt.savefig(comparison_plot_file, dpi=150, bbox_inches="tight")
        print(f"✓ Saved comparison plot: {comparison_plot_file}")
        plt.show()

    except Exception as e:
        print(f"Warning: Visualization failed: {e}")

    print()


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
    colors = ["red", "blue", "green", "orange", "purple", "brown", "pink"]

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
    if legend_elements:
        ax.legend(handles=legend_elements, loc="best", fontsize="small")


if __name__ == "__main__":
    main()
    show_cli_equivalents()
