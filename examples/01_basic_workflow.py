#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Basic Workflow Example - Delhi Road Sampling

This example demonstrates the complete end-to-end workflow for extracting
and sampling road segments from Delhi, India using both the Python API
and CLI commands of the geo_sampling package.

The workflow includes:
1. Extracting all road segments from Delhi
2. Randomly sampling 1000 road segments
3. Visualizing the results
4. Saving the data to CSV
5. Showing equivalent CLI commands

NETWORK REQUIRED: This example requires an active internet connection to download
geographic data from BBBike.org and GADM. The example will fail if the network
is unavailable.

OUTPUT: Results are saved to examples/outputs/01_basic_workflow/
"""

import os
import time
import geo_sampling as gs


def show_cli_equivalent():
    """Show equivalent CLI commands for this workflow."""
    print("\n" + "=" * 60)
    print("EQUIVALENT CLI COMMANDS")
    print("=" * 60)

    print("To reproduce this workflow using the command line:\n")

    print("# Option 1: Full workflow in one command")
    print('geo-sampling workflow "India" "NCT of Delhi" \\')
    print("    --sample-size 1000 \\")
    print(
        "    --output examples/outputs/01_basic_workflow/delhi_workflow_sample.csv \\"
    )
    print("    --plot \\")
    print("    --seed 42")
    print()

    print("# Option 2: Step-by-step approach")
    print("# Step 1: Extract all roads")
    print('geo-sampling extract "India" "NCT of Delhi" \\')
    print("    --output examples/outputs/01_basic_workflow/delhi_all_roads.csv")
    print()
    print("# Step 2: Sample from extracted roads")
    print(
        "geo-sampling sample examples/outputs/01_basic_workflow/delhi_all_roads.csv \\"
    )
    print("    --sample-size 1000 \\")
    print("    --strategy random \\")
    print("    --seed 42 \\")
    print("    --output examples/outputs/01_basic_workflow/delhi_sampled_roads.csv \\")
    print("    --plot")
    print()

    print("# Step 3: Get information about the region")
    print('geo-sampling info "India" "NCT of Delhi"')
    print()


def main():
    """Execute the basic workflow example."""
    print("=" * 60)
    print("Basic Workflow Example: Delhi Road Sampling")
    print("=" * 60)

    # Configuration
    country = "India"
    region = "NCT of Delhi"
    admin_level = 1
    sample_size = 1000

    # Create output directory structure
    output_dir = "examples/outputs/01_basic_workflow"
    os.makedirs(output_dir, exist_ok=True)

    # Output files
    all_roads_file = os.path.join(output_dir, "delhi_all_roads.csv")
    sampled_roads_file = os.path.join(output_dir, "delhi_sampled_roads.csv")

    print(f"Region: {region}, {country}")
    print(f"Sample size: {sample_size}")
    print()

    # Step 1: Extract all road segments
    print("Step 1: Extracting road segments...")
    start_time = time.time()

    try:
        # Create extractor
        extractor = gs.RoadExtractor(country, region, admin_level)

        # Extract all roads
        all_roads = extractor.get_roads()

        extraction_time = time.time() - start_time
        print(f"✓ Extracted {len(all_roads)} road segments in {extraction_time:.1f}s")

        # Show road type summary
        sampler = gs.RoadSampler(all_roads)
        road_summary = sampler.get_road_type_summary()
        print(f"Road types found: {dict(road_summary)}")
        print()

    except Exception as e:
        print(f"✗ Failed to extract roads: {e}")
        print("Check your internet connection and try again.")
        return

    # Step 2: Sample road segments
    print("Step 2: Sampling road segments...")
    start_time = time.time()

    # Random sampling with seed for reproducibility
    sample = sampler.random_sample(sample_size, seed=42)

    sampling_time = time.time() - start_time
    print(f"✓ Sampled {len(sample)} segments in {sampling_time:.3f}s")

    # Show sample summary
    sample_summary = gs.RoadSampler(sample).get_road_type_summary()
    print(f"Sample road types: {dict(sample_summary)}")
    print()

    # Step 3: Save data
    print("Step 3: Saving data...")

    # Save all roads
    sampler.save_csv(all_roads, all_roads_file)
    print(f"✓ Saved all roads to: {all_roads_file}")

    # Save sample
    sampler.save_csv(sample, sampled_roads_file)
    print(f"✓ Saved sample to: {sampled_roads_file}")
    print()

    # Step 4: Visualize results
    print("Step 4: Creating visualizations...")

    try:
        import matplotlib.pyplot as plt

        # Plot sample and save
        print("Creating sample plot...")
        fig, ax = plt.subplots(figsize=(12, 8))
        gs.plot_road_segments(sample, title=f"Delhi Road Sample (N={len(sample)})")
        sample_plot_file = os.path.join(output_dir, "delhi_sample_plot.png")
        plt.savefig(sample_plot_file, dpi=150, bbox_inches="tight")
        print(f"✓ Saved sample plot to: {sample_plot_file}")

        # Plot with comparison (if reasonable size)
        if len(all_roads) < 10000:  # Only if dataset is manageable
            print("Creating comparison plot...")
            comparison_plot_file = os.path.join(output_dir, "delhi_comparison_plot.png")
            plotter = gs.RoadPlotter(figsize=(16, 8))
            plotter.plot_sample_comparison(all_roads, sample)
            plt.savefig(comparison_plot_file, dpi=150, bbox_inches="tight")
            print(f"✓ Saved comparison plot to: {comparison_plot_file}")
        else:
            print(
                f"Skipping comparison plot (dataset too large: {len(all_roads)} segments)"
            )

        plt.show()

    except Exception as e:
        print(f"Warning: Visualization failed: {e}")
        print("Data extraction and sampling completed successfully.")

    # Step 5: Summary statistics
    print()
    print("=" * 60)
    print("RESULTS SUMMARY")
    print("=" * 60)
    print(f"Total road segments extracted: {len(all_roads)}")
    print(f"Sample size: {len(sample)}")
    print(f"Sampling ratio: {len(sample) / len(all_roads) * 100:.1f}%")
    print()
    print("Files created:")
    print(f"  - {all_roads_file} ({os.path.getsize(all_roads_file) / 1024:.1f} KB)")
    print(
        f"  - {sampled_roads_file} ({os.path.getsize(sampled_roads_file) / 1024:.1f} KB)"
    )
    print()

    # Example of loading data back
    print("Verification: Loading sample back from CSV...")
    loaded_sample = gs.load_segments_from_csv(sampled_roads_file)
    print(f"✓ Successfully loaded {len(loaded_sample)} segments from CSV")

    # Quick validation
    if len(loaded_sample) == len(sample):
        print("✓ Data integrity verified")
    else:
        print("✗ Data integrity check failed")

    print("\nExample completed successfully!")


def demonstrate_convenience_api():
    """Demonstrate the high-level convenience API."""
    print("\n" + "=" * 60)
    print("BONUS: High-level API Demonstration")
    print("=" * 60)

    print("Using the convenience function for quick sampling...")

    try:
        # One-liner sampling
        quick_sample = gs.sample_roads_for_region(
            "India", "NCT of Delhi", n=100, admin_level=1, seed=42
        )

        print(f"✓ Quick sample of {len(quick_sample)} segments")
        print(f"Sample types: {set(s.osm_type for s in quick_sample)}")

        # Quick plot
        gs.quick_plot(quick_sample, title="Quick API Sample")

    except Exception as e:
        print(f"Convenience API failed: {e}")
        print("Network-dependent functionality requires internet connection.")


if __name__ == "__main__":
    # Run basic workflow
    main()

    # Show CLI equivalents
    show_cli_equivalent()

    # Demonstrate convenience API
    demonstrate_convenience_api()
