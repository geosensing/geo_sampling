```{include} _includes/quickstart.md
```

## Understanding the Output

### CSV File Structure

The output CSV contains these columns:

| Column | Description |
|--------|-------------|
| `segment_id` | Unique identifier for each road segment |
| `osm_id` | OpenStreetMap way ID |
| `osm_name` | Road name from OpenStreetMap |
| `osm_type` | Road type (primary, secondary, residential, etc.) |
| `start_lat`, `start_long` | Starting coordinates of segment |
| `end_lat`, `end_long` | Ending coordinates of segment |

### Sample Data

Here's what a few rows look like:

```csv
segment_id,osm_id,osm_name,osm_type,start_lat,start_long,end_lat,end_long
1,way_123,Orchard Road,primary,1.3048,103.8318,1.3052,103.8322
2,way_124,Marina Bay Drive,trunk,1.2966,103.8558,1.2970,103.8562
3,way_125,Residential Street,residential,1.3100,103.8400,1.3104,103.8404
```

### Working with Sample Data

Load and analyze your samples:

```python
import geo_sampling as gs
import pandas as pd

# Load the CSV back into Python
segments = gs.load_segments_from_csv("singapore_sample.csv")
print(f"Loaded {len(segments)} segments")

# Convert to pandas DataFrame for analysis (optional)
sampler = gs.RoadSampler(segments)
df = sampler.to_dataframe()

# Analyze road type distribution
road_type_counts = df['osm_type'].value_counts()
print("Road type distribution:")
print(road_type_counts)
```

## Common Workflows

### Research Study Design

```python
import geo_sampling as gs

# 1. Get road summary to plan sample size
summary = gs.get_road_summary("Thailand", "Bangkok")
print(f"Total roads available: {summary['total_segments']:,}")
print("Road types:", list(summary['road_types']))

# 2. Extract and sample with stratification
sample = gs.sample_roads_for_region(
    "Thailand", "Bangkok",
    n=500,  # Sample size
    strategy="stratified",  # Maintain road type proportions
    road_types=["primary", "secondary", "tertiary"],  # Focus on major roads
    seed=42  # Reproducible results
)

# 3. Export for field work
sampler = gs.RoadSampler(sample)
sampler.save_csv(sample, "bangkok_fieldwork_sample.csv")

# 4. Create field maps
gs.plot_road_segments(sample, title="Bangkok Field Study Sites")
```

### Batch Processing Multiple Regions

```bash
#!/bin/bash
# Process multiple regions

REGIONS=("Bangkok" "Chiang Mai" "Phuket")

for region in "${REGIONS[@]}"; do
    echo "Processing $region..."

    geo-sampling workflow "Thailand" "$region" \
        --sample-size 200 \
        --strategy stratified \
        --output "${region,,}_sample.csv" \
        --plot
done
```

## Tips for Success

### 1. Start Small
Begin with small administrative areas to test your workflow before scaling up.

### 2. Check Data Quality
Always inspect a few segments manually:
```python
# Look at first few segments
for i, seg in enumerate(sample[:3]):
    print(f"Segment {i+1}: {seg.osm_name} ({seg.osm_type})")
    print(f"  From: {seg.start_lat:.4f}, {seg.start_long:.4f}")
    print(f"  To: {seg.end_lat:.4f}, {seg.end_long:.4f}")
```

### 3. Validate Geographic Bounds
Plot samples to ensure they cover your intended study area:
```python
gs.quick_plot(sample, title="Sample Coverage Check")
```

### 4. Document Your Methodology
Save your sampling parameters for reproducibility:
```python
import json

metadata = {
    "country": "Singapore",
    "region": "Central",
    "sample_size": len(sample),
    "strategy": "stratified",
    "road_types": ["primary", "secondary"],
    "seed": 42,
    "date_created": "2024-01-15"
}

with open("sample_metadata.json", "w") as f:
    json.dump(metadata, f, indent=2)
```

## Troubleshooting

**Empty results**: Check that your region name matches exactly what's in GADM. Use `geo-sampling info` to verify.

**Too many segments**: Use road type filtering or smaller administrative areas to reduce the sampling frame.

**Plotting issues**: Install matplotlib if you get visualization errors: `pip install matplotlib`

## Next Steps

Ready for more advanced usage? Check out:

- 🎯 [Advanced Sampling Strategies](examples/advanced.md)
- 💻 [Complete CLI Reference](examples/cli-usage.md)
- 🐍 [Python API Examples](examples/python-api.md)
