#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI Usage Examples

This script demonstrates how to use the geo_sampling command-line interface
and shows equivalent Python API calls for each CLI command.

The CLI provides four main commands:
1. extract - Extract road segments from a region
2. sample - Sample from existing road data
3. workflow - Complete extraction and sampling pipeline
4. info - Get information about regions and road types

NETWORK REQUIRED: The actual CLI commands shown require an active internet
connection to download geographic data from BBBike.org and GADM. This script
demonstrates the command syntax without executing network-dependent operations.
"""

import subprocess
import sys


def show_cli_help():
    """Show main CLI help."""
    print("=" * 60)
    print("CLI Help and Available Commands")
    print("=" * 60)

    print("Main command help:")
    print("$ geo-sampling --help")
    print()

    # Show actual help if available
    try:
        result = subprocess.run(
            [sys.executable, "-m", "geo_sampling.cli", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode == 0:
            print("Actual output:")
            print(result.stdout)
        else:
            print("CLI help not available in this environment")
    except Exception:
        print("CLI help not available in this environment")

    print()


def demonstrate_extract_command():
    """Demonstrate the extract command."""
    print("=" * 60)
    print("1. EXTRACT COMMAND")
    print("=" * 60)

    print("Extract all roads from Delhi, India:")
    cli_cmd = 'geo-sampling extract "India" "NCT of Delhi" --output delhi_roads.csv'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
import geo_sampling as gs

# Extract roads
extractor = gs.RoadExtractor("India", "NCT of Delhi")
roads = extractor.get_roads()

# Save to CSV
extractor.save_csv("delhi_roads.csv")
print(f"Extracted {len(roads)} road segments")
"""
    print(python_code)

    print("\nExtract only major roads:")
    cli_cmd = 'geo-sampling extract "India" "NCT of Delhi" --road-types primary --road-types secondary --road-types trunk --output delhi_major_roads.csv'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
# Extract filtered roads
roads = extractor.get_roads(road_types=["primary", "secondary", "trunk"])
extractor.save_csv("delhi_major_roads.csv", road_types=["primary", "secondary", "trunk"])
"""
    print(python_code)
    print()


def demonstrate_sample_command():
    """Demonstrate the sample command."""
    print("=" * 60)
    print("2. SAMPLE COMMAND")
    print("=" * 60)

    print("Random sample of 1000 segments:")
    cli_cmd = "geo-sampling sample delhi_roads.csv --sample-size 1000 --strategy random --output delhi_sample_1000.csv"
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
import geo_sampling as gs

# Load roads from CSV
roads = gs.load_segments_from_csv("delhi_roads.csv")

# Random sampling
sampler = gs.RoadSampler(roads)
sample = sampler.random_sample(1000, seed=42)

# Save sample
sampler.save_csv(sample, "delhi_sample_1000.csv")
"""
    print(python_code)

    print("\nStratified sample maintaining proportions:")
    cli_cmd = "geo-sampling sample delhi_roads.csv --sample-size 500 --strategy stratified --seed 42 --output delhi_stratified_500.csv"
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
# Stratified sampling
sample = sampler.stratified_sample(500, seed=42)
sampler.save_csv(sample, "delhi_stratified_500.csv")
"""
    print(python_code)

    print("\nSample only specific road types:")
    cli_cmd = "geo-sampling sample delhi_roads.csv --sample-size 200 --road-types primary --road-types secondary --output delhi_primary_secondary.csv"
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
# Filtered sampling
sample = sampler.random_sample(200, road_types=["primary", "secondary"], seed=42)
sampler.save_csv(sample, "delhi_primary_secondary.csv")
"""
    print(python_code)
    print()


def demonstrate_workflow_command():
    """Demonstrate the workflow command (extract + sample)."""
    print("=" * 60)
    print("3. WORKFLOW COMMAND (Extract + Sample)")
    print("=" * 60)

    print("Complete workflow in one command:")
    cli_cmd = 'geo-sampling workflow "Singapore" "Central" --sample-size 100 --strategy random --output singapore_sample.csv'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
import geo_sampling as gs

# One-liner using convenience function
sample = gs.sample_roads_for_region(
    "Singapore", "Central",
    n=100,
    admin_level=1,
    strategy="random",
    seed=42
)

# Save sample
sampler = gs.RoadSampler(sample)
sampler.save_csv(sample, "singapore_sample.csv")
"""
    print(python_code)

    print("\nWorkflow with visualization:")
    cli_cmd = 'geo-sampling workflow "Singapore" "Central" --sample-size 100 --plot --output singapore_sample.csv'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
# Workflow with plotting
sample = gs.sample_roads_for_region("Singapore", "Central", n=100)

# Plot results
gs.plot_road_segments(sample, title="Singapore Road Sample")

# Or use quick plot
gs.quick_plot(sample, title="Singapore Sample")
"""
    print(python_code)
    print()


def demonstrate_info_command():
    """Demonstrate the info command."""
    print("=" * 60)
    print("4. INFO COMMAND")
    print("=" * 60)

    print("Get road information for a region:")
    cli_cmd = 'geo-sampling info "Thailand" "Bangkok"'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
import geo_sampling as gs

# Get road summary for a region
summary = gs.get_road_summary("Thailand", "Bangkok", admin_level=1)
print(f"Total segments: {summary['total_segments']:,}")
print(f"Road types: {summary['road_types']}")
print(f"Road type breakdown: {summary['road_type_counts']}")
"""
    print(python_code)

    print("\nGet info with custom admin level:")
    cli_cmd = 'geo-sampling info "Thailand" "Bangkok" --admin-level 2'
    print(f"CLI: {cli_cmd}")

    print("\nEquivalent Python API:")
    python_code = """
# Get summary at different administrative level
summary = gs.get_road_summary("Thailand", "Bangkok", admin_level=2)
print("Road summary at admin level 2:", summary)
"""
    print(python_code)
    print()


def demonstrate_advanced_cli_usage():
    """Demonstrate advanced CLI patterns."""
    print("=" * 60)
    print("5. ADVANCED CLI PATTERNS")
    print("=" * 60)

    print("Chaining commands with shell pipes:")

    # Extract then sample
    commands = [
        'geo-sampling extract "India" "NCT of Delhi" --output delhi.csv',
        "geo-sampling sample delhi.csv --sample-size 1000 --output delhi_1k.csv",
        'geo-sampling info "India" "NCT of Delhi"',
    ]

    print("# Extract, then sample, then analyze")
    for cmd in commands:
        print(f"{cmd}")

    print("\nBatch processing multiple regions:")
    batch_script = """#!/bin/bash
# Batch process multiple regions

COUNTRIES=("Singapore" "Thailand" "India")
REGIONS=("Central" "Trang" "NCT of Delhi")

for i in ${!COUNTRIES[@]}; do
    country=${COUNTRIES[$i]}
    region=${REGIONS[$i]}
    output="${country,,}_${region,,// /_}.csv"

    echo "Processing $country - $region..."
    geo-sampling workflow \\
        "$country" \\
        "$region" \\
        --sample-size 500 \\
        --output "$output" \\
        --plot
done
"""
    print(batch_script)

    print("\nEquivalent Python batch processing:")
    python_batch = """
import geo_sampling as gs

regions = [
    ("Singapore", "Central"),
    ("Thailand", "Trang"),
    ("India", "NCT of Delhi")
]

for country, region in regions:
    output = f"{country.lower()}_{region.lower().replace(' ', '_')}.csv"

    print(f"Processing {country} - {region}...")
    sample = gs.sample_roads_for_region(country, region, n=500)

    sampler = gs.RoadSampler(sample)
    sampler.save_csv(sample, output)

    gs.plot_road_segments(sample, title=f"{country} - {region}")
"""
    print(python_batch)
    print()


def show_complete_example():
    """Show a complete realistic example."""
    print("=" * 60)
    print("6. COMPLETE REALISTIC EXAMPLE")
    print("=" * 60)

    print(
        "Research scenario: Sampling roads in multiple Thai provinces for field survey"
    )
    print()

    print("Step 1: Extract roads from multiple provinces")
    commands = [
        'geo-sampling extract "Thailand" "Trang" --road-types primary --road-types secondary --road-types tertiary --output trang_roads.csv',
        'geo-sampling extract "Thailand" "Phuket" --road-types primary --road-types secondary --road-types tertiary --output phuket_roads.csv',
        'geo-sampling extract "Thailand" "Krabi" --road-types primary --road-types secondary --road-types tertiary --output krabi_roads.csv',
    ]

    for cmd in commands:
        print(f"$ {cmd}")

    print("\nStep 2: Sample from each province")
    sample_commands = [
        "geo-sampling sample trang_roads.csv --sample-size 200 --strategy stratified --output trang_sample.csv",
        "geo-sampling sample phuket_roads.csv --sample-size 150 --strategy stratified --output phuket_sample.csv",
        "geo-sampling sample krabi_roads.csv --sample-size 100 --strategy stratified --output krabi_sample.csv",
    ]

    for cmd in sample_commands:
        print(f"$ {cmd}")

    print("\nStep 3: Analyze the samples")
    analyze_commands = [
        'geo-sampling info "Thailand" "Trang"',
        'geo-sampling info "Thailand" "Phuket"',
        'geo-sampling info "Thailand" "Krabi"',
    ]

    for cmd in analyze_commands:
        print(f"$ {cmd}")

    print("\nEquivalent Python research workflow:")
    research_code = """
import geo_sampling as gs
import pandas as pd

# Research configuration
provinces = ["Trang", "Phuket", "Krabi"]
sample_sizes = [200, 150, 100]
road_types = ["primary", "secondary", "tertiary"]

all_samples = []

for province, n in zip(provinces, sample_sizes):
    print(f"Processing {province}...")

    # Extract roads
    extractor = gs.RoadExtractor("Thailand", province, admin_level=1)
    roads = extractor.get_roads(road_types=road_types)

    # Stratified sampling to maintain road type proportions
    sampler = gs.RoadSampler(roads)
    sample = sampler.stratified_sample(n, seed=42)

    # Add province information
    for segment in sample:
        segment.province = province  # Custom attribute

    all_samples.extend(sample)

    # Save individual province samples
    sampler.save_csv(sample, f"{province.lower()}_sample.csv")

    # Quick analysis
    summary = sampler.get_road_type_summary()
    print(f"  {province}: {dict(summary)}")

# Combined analysis
print(f"\\nTotal sample size: {len(all_samples)}")

# Save combined sample
combined_sampler = gs.RoadSampler(all_samples)
combined_sampler.save_csv(all_samples, "thailand_combined_sample.csv")

# Visualization
gs.plot_road_segments(all_samples, title="Thailand Multi-Province Road Sample")
"""
    print(research_code)


def main():
    """Run all CLI demonstrations."""
    print("GEO_SAMPLING CLI Usage Examples")
    print("This script shows CLI commands and equivalent Python API usage")
    print("Note: Commands are shown for demonstration - not executed")
    print()

    show_cli_help()
    demonstrate_extract_command()
    demonstrate_sample_command()
    demonstrate_workflow_command()
    demonstrate_info_command()
    demonstrate_advanced_cli_usage()
    show_complete_example()

    print("=" * 60)
    print("CLI EXAMPLES COMPLETE")
    print("=" * 60)
    print("To run any of these commands:")
    print("1. Install the package: pip install geo-sampling")
    print("2. Run commands in your terminal")
    print("3. Or use the equivalent Python API in your scripts")
    print()
    print("For more help: geo-sampling --help")


if __name__ == "__main__":
    main()
