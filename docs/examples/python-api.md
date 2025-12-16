# Python API Examples

This page demonstrates the Python API with **real, working examples** using actual OpenStreetMap data. All code examples are executable and produce the output files you can download.

## Basic Workflow Example

This example shows the complete end-to-end workflow using Delhi, India data.

### The Complete Workflow

```python
#!/usr/bin/env python3
"""
Basic Workflow Example - Delhi Road Sampling

This example demonstrates extracting and sampling road segments from Delhi, India
using both the Python API and CLI commands.
"""

import os
import geo_sampling as gs

def main():
    # Configuration
    country = "India"
    region = "NCT of Delhi"
    sample_size = 1000

    # Create output directory
    output_dir = "examples/outputs/01_basic_workflow"
    os.makedirs(output_dir, exist_ok=True)

    print(f"Extracting roads for {region}, {country}...")

    # Step 1: Extract all road segments
    extractor = gs.RoadExtractor(country, region)
    all_roads = extractor.get_roads()
    print(f"✓ Extracted {len(all_roads)} road segments")

    # Step 2: Random sampling
    sampler = gs.RoadSampler(all_roads)
    sample = sampler.random_sample(sample_size, seed=42)
    print(f"✓ Sampled {len(sample)} segments")

    # Step 3: Save outputs
    all_roads_file = os.path.join(output_dir, "delhi_all_roads.csv")
    sample_file = os.path.join(output_dir, "delhi_sampled_roads.csv")

    sampler.save_csv(all_roads, all_roads_file)
    sampler.save_csv(sample, sample_file)
    print(f"✓ Saved outputs to {output_dir}")

    # Step 4: Visualize results
    gs.plot_road_segments(sample, title=f"Delhi Road Sample (N={len(sample)})")

    # Summary statistics
    road_summary = sampler.get_road_type_summary()
    print("Road type distribution:", dict(road_summary))

if __name__ == "__main__":
    main()
```

### Generated Outputs

This example produces real files you can examine:

::::{grid} 1 1 2 2
:gutter: 2

:::{grid-item}
**📄 delhi_all_roads.csv**
- **Size**: 1,220 road segments
- **Coverage**: Complete NCT of Delhi road network
- **Types**: All road types (trunk, primary, residential, etc.)
- [📥 Download](../../examples/outputs/01_basic_workflow/delhi_all_roads.csv)
:::

:::{grid-item}
**📄 delhi_sampled_roads.csv**
- **Size**: 1,000 randomly sampled segments
- **Method**: Random sampling with seed=42
- **Use**: Ready for field data collection
- [📥 Download](../../examples/outputs/01_basic_workflow/delhi_sampled_roads.csv)
:::

:::{grid-item}
**🖼️ delhi_sample_plot.png**
- **Type**: Geographic visualization
- **Shows**: Sample distribution across Delhi
- **Format**: High-resolution PNG
- [📥 View Plot](../../examples/outputs/01_basic_workflow/delhi_sample_plot.png)
:::

:::{grid-item}
**🖼️ delhi_comparison_plot.png**
- **Type**: Side-by-side comparison
- **Shows**: All roads vs. sample
- **Purpose**: Validate sampling coverage
- [📥 View Plot](../../examples/outputs/01_basic_workflow/delhi_comparison_plot.png)
:::
::::

### CLI Equivalent Commands

The same workflow using command-line interface:

```bash
# Option 1: Complete workflow in one command
geo-sampling workflow "India" "NCT of Delhi" \
    --sample-size 1000 \
    --output delhi_workflow_sample.csv \
    --plot \
    --seed 42

# Option 2: Step-by-step approach
# Extract all roads
geo-sampling extract "India" "NCT of Delhi" \
    --output delhi_all_roads.csv

# Create random sample
geo-sampling sample delhi_all_roads.csv \
    --sample-size 1000 \
    --strategy random \
    --seed 42 \
    --output delhi_sampled_roads.csv \
    --plot

# Get region information
geo-sampling info "India" "NCT of Delhi"
```

## Advanced Python API Features

### Convenience Functions

For quick research tasks, use the high-level convenience API:

```python
import geo_sampling as gs

# One-liner for quick sampling
sample = gs.sample_roads_for_region(
    "India", "NCT of Delhi",
    n=1000,
    admin_level=1,
    seed=42
)

# Quick plotting
gs.quick_plot(sample, title="Delhi Sample")

# Get region summary without full extraction
summary = gs.get_road_summary("India", "NCT of Delhi")
print(f"Total roads: {summary['total_segments']:,}")
print(f"Road types: {summary['road_types']}")
```

### Working with Road Types

Filter by specific road types for focused sampling:

```python
# Extract only major roads
extractor = gs.RoadExtractor("India", "NCT of Delhi")
major_roads = extractor.get_roads(
    road_types=["trunk", "primary", "secondary"]
)

print(f"Major roads: {len(major_roads)} segments")

# Sample from major roads only
sampler = gs.RoadSampler(major_roads)
major_sample = sampler.random_sample(500, seed=42)

# Road type distribution
road_summary = sampler.get_road_type_summary()
for road_type, count in road_summary.items():
    percentage = count / len(major_roads) * 100
    print(f"{road_type}: {count} ({percentage:.1f}%)")
```

### Integration Examples

#### Research Workflow Integration

```python
import geo_sampling as gs
import pandas as pd
import json
from datetime import datetime

def research_sampling_workflow(country, region, sample_size, study_name):
    """Complete research workflow with metadata tracking."""

    # Track methodology
    metadata = {
        "study_name": study_name,
        "country": country,
        "region": region,
        "sample_size": sample_size,
        "date_created": datetime.now().isoformat(),
        "methodology": "stratified_sampling"
    }

    # Extract and sample
    sample = gs.sample_roads_for_region(
        country, region,
        n=sample_size,
        strategy="stratified",
        seed=42
    )

    # Convert to DataFrame for analysis
    sampler = gs.RoadSampler(sample)
    df = sampler.to_dataframe()

    # Add study metadata to DataFrame
    df['study_id'] = study_name
    df['sample_date'] = metadata['date_created']

    # Save with metadata
    output_file = f"{study_name.lower().replace(' ', '_')}_sample.csv"
    df.to_csv(output_file, index=False)

    # Save metadata
    with open(f"{study_name.lower().replace(' ', '_')}_metadata.json", "w") as f:
        json.dump(metadata, f, indent=2)

    print(f"Study '{study_name}' complete:")
    print(f"  Sample size: {len(sample)}")
    print(f"  Output: {output_file}")
    print(f"  Road types: {df['osm_type'].nunique()}")

    return df

# Run research workflow
study_data = research_sampling_workflow(
    "Thailand", "Bangkok",
    sample_size=500,
    study_name="Bangkok Traffic Study 2024"
)
```

#### Batch Processing Multiple Regions

```python
import geo_sampling as gs

def batch_process_regions(regions, sample_size=200):
    """Process multiple regions with consistent methodology."""

    results = {}

    for country, region in regions:
        print(f"Processing {region}, {country}...")

        try:
            # Sample roads
            sample = gs.sample_roads_for_region(
                country, region,
                n=sample_size,
                strategy="stratified",
                seed=42
            )

            # Save output
            filename = f"{country.lower()}_{region.lower().replace(' ', '_')}.csv"
            sampler = gs.RoadSampler(sample)
            sampler.save_csv(sample, filename)

            # Track results
            results[f"{country}-{region}"] = {
                "sample_size": len(sample),
                "filename": filename,
                "road_types": len(sampler.get_road_type_summary())
            }

            print(f"  ✓ {len(sample)} segments → {filename}")

        except Exception as e:
            print(f"  ✗ Failed: {e}")
            results[f"{country}-{region}"] = {"error": str(e)}

    return results

# Process multiple regions
regions = [
    ("Singapore", "Central"),
    ("Thailand", "Bangkok"),
    ("India", "NCT of Delhi")
]

batch_results = batch_process_regions(regions, sample_size=300)

# Summary
print("\nBatch Processing Results:")
for region, result in batch_results.items():
    if "error" in result:
        print(f"  ❌ {region}: {result['error']}")
    else:
        print(f"  ✅ {region}: {result['sample_size']} segments, {result['road_types']} road types")
```

### Data Analysis Integration

#### Working with Pandas

```python
import geo_sampling as gs
import pandas as pd
import matplotlib.pyplot as plt

# Load sample data
segments = gs.load_segments_from_csv("delhi_sampled_roads.csv")
sampler = gs.RoadSampler(segments)

# Convert to DataFrame for analysis
df = sampler.to_dataframe()

# Analyze road type distribution
road_counts = df['osm_type'].value_counts()
print("Road Type Distribution:")
print(road_counts)

# Calculate segment lengths (rough approximation)
df['length_km'] = ((df['end_lat'] - df['start_lat'])**2 +
                   (df['end_long'] - df['start_long'])**2)**0.5 * 111.32

# Summary statistics by road type
summary_stats = df.groupby('osm_type').agg({
    'length_km': ['count', 'mean', 'sum'],
    'start_lat': ['min', 'max'],
    'start_long': ['min', 'max']
}).round(3)

print("\nSummary by Road Type:")
print(summary_stats)

# Visualization
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 6))

# Road type distribution
road_counts.plot(kind='bar', ax=ax1)
ax1.set_title('Road Type Distribution')
ax1.set_ylabel('Number of Segments')

# Length distribution
df.boxplot(column='length_km', by='osm_type', ax=ax2)
ax2.set_title('Segment Length by Road Type')
ax2.set_ylabel('Length (km)')

plt.tight_layout()
plt.show()
```

## Next Steps

- 🎯 Explore [Advanced Sampling Strategies](advanced.md)
- 💻 Learn the [Command Line Interface](cli-usage.md)
- 📚 Check the [API Reference](../reference/index.md)
- 📁 Download [all example outputs](../../examples/outputs/)

## Source Code

The complete source code for these examples is available:
- [01_basic_workflow.py](../../examples/01_basic_workflow.py)
- [02_advanced_sampling.py](../../examples/02_advanced_sampling.py)
- [generate_sample_outputs.py](../../examples/generate_sample_outputs.py)
