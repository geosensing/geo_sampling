# Advanced Sampling Strategies

This guide covers sophisticated sampling techniques for complex research designs.

## Stratified Sampling by Road Type

When you need representative samples from different road categories:

```python
from geo_sampling import sample_roads

# Sample with specific proportions
sample_roads.sample_roads(
    'delhi_roads.csv',
    'delhi_stratified.csv',
    sample_size=1000,
    stratify_by='road_type',
    strata_proportions={
        'motorway': 0.1,
        'primary': 0.2,
        'secondary': 0.3,
        'residential': 0.4
    }
)
```

## Geographic Clustering

For studies requiring spatial clusters:

```python
import pandas as pd
from sklearn.cluster import KMeans
from geo_sampling import sample_roads

# Load road data
roads = pd.read_csv('roads.csv')

# Create geographic clusters
coords = roads[['latitude', 'longitude']].values
kmeans = KMeans(n_clusters=10, random_state=42)
roads['cluster'] = kmeans.fit_predict(coords)

# Sample from each cluster
samples = []
for cluster_id in range(10):
    cluster_roads = roads[roads['cluster'] == cluster_id]
    cluster_sample = cluster_roads.sample(n=50, random_state=42)
    samples.append(cluster_sample)

final_sample = pd.concat(samples)
final_sample.to_csv('clustered_sample.csv', index=False)
```

## Time-Based Sampling

For longitudinal studies with repeated measurements:

```python
import numpy as np

# Define sampling waves
n_waves = 4
samples_per_wave = 250
total_roads = len(roads)

# Generate non-overlapping samples
all_indices = np.arange(total_roads)
np.random.shuffle(all_indices)

wave_size = total_roads // n_waves
for wave in range(n_waves):
    start_idx = wave * wave_size
    end_idx = start_idx + wave_size
    wave_indices = all_indices[start_idx:end_idx]

    # Sample from this wave's pool
    wave_sample = np.random.choice(wave_indices,
                                  size=samples_per_wave,
                                  replace=False)

    wave_roads = roads.iloc[wave_sample]
    wave_roads.to_csv(f'wave_{wave+1}_sample.csv', index=False)
```

## Weighted Sampling by Traffic Density

Weight samples by estimated traffic volume:

```python
# Assign weights based on road type
road_weights = {
    'motorway': 10.0,
    'trunk': 8.0,
    'primary': 6.0,
    'secondary': 4.0,
    'tertiary': 2.0,
    'residential': 1.0
}

roads['weight'] = roads['road_type'].map(road_weights).fillna(0.5)

# Weighted random sampling
sample = roads.sample(
    n=500,
    weights='weight',
    random_state=42
)
sample.to_csv('traffic_weighted_sample.csv', index=False)
```

## Exclusion Zones

Exclude areas near specific points of interest:

```python
from shapely.geometry import Point
from shapely.ops import unary_union

# Define exclusion zones (e.g., around hospitals, schools)
exclusion_points = [
    (28.6139, 77.2090),  # Point of interest 1
    (28.5355, 77.3910),  # Point of interest 2
]

# Create buffer zones (1km radius)
exclusion_zones = []
for lat, lon in exclusion_points:
    point = Point(lon, lat)
    buffer = point.buffer(0.01)  # ~1km in degrees
    exclusion_zones.append(buffer)

combined_exclusion = unary_union(exclusion_zones)

# Filter roads outside exclusion zones
valid_roads = []
for idx, row in roads.iterrows():
    road_point = Point(row['longitude'], row['latitude'])
    if not combined_exclusion.contains(road_point):
        valid_roads.append(row)

filtered_roads = pd.DataFrame(valid_roads)
sample = filtered_roads.sample(n=500, random_state=42)
```

## Multi-Stage Sampling

Hierarchical sampling approach:

```python
# Stage 1: Sample districts
districts = roads['district'].unique()
sampled_districts = np.random.choice(districts, size=5, replace=False)

# Stage 2: Sample neighborhoods within districts
stage2_roads = roads[roads['district'].isin(sampled_districts)]
neighborhoods = stage2_roads.groupby('district')['neighborhood'].unique()

sampled_neighborhoods = []
for district in sampled_districts:
    district_neighborhoods = neighborhoods[district]
    sampled = np.random.choice(district_neighborhoods,
                             size=min(3, len(district_neighborhoods)),
                             replace=False)
    sampled_neighborhoods.extend(sampled)

# Stage 3: Sample roads within neighborhoods
final_roads = roads[roads['neighborhood'].isin(sampled_neighborhoods)]
final_sample = final_roads.sample(n=min(500, len(final_roads)),
                                 random_state=42)
final_sample.to_csv('multi_stage_sample.csv', index=False)
```

## Validation and Quality Checks

Always validate your samples:

```python
def validate_sample(sample_df, original_df):
    """Validate sample representativeness"""

    print("Sample Validation Report")
    print("=" * 40)

    # Sample size
    print(f"Sample size: {len(sample_df)}")
    print(f"Original size: {len(original_df)}")
    print(f"Sampling rate: {len(sample_df)/len(original_df):.2%}")

    # Road type distribution
    print("\nRoad Type Distribution:")
    sample_dist = sample_df['road_type'].value_counts(normalize=True)
    original_dist = original_df['road_type'].value_counts(normalize=True)

    comparison = pd.DataFrame({
        'Sample': sample_dist,
        'Original': original_dist,
        'Difference': sample_dist - original_dist
    })
    print(comparison)

    # Geographic spread
    print("\nGeographic Coverage:")
    print(f"Latitude range - Sample: [{sample_df['latitude'].min():.4f}, "
          f"{sample_df['latitude'].max():.4f}]")
    print(f"Latitude range - Original: [{original_df['latitude'].min():.4f}, "
          f"{original_df['latitude'].max():.4f}]")

    print(f"Longitude range - Sample: [{sample_df['longitude'].min():.4f}, "
          f"{sample_df['longitude'].max():.4f}]")
    print(f"Longitude range - Original: [{original_df['longitude'].min():.4f}, "
          f"{original_df['longitude'].max():.4f}]")

    return comparison

# Run validation
validation_results = validate_sample(sample, roads)
```

## Best Practices

1. **Document your sampling strategy** - Include rationale for choices
2. **Set random seeds** - Ensure reproducibility
3. **Validate samples** - Check representativeness
4. **Handle edge cases** - Account for missing data or small strata
5. **Consider field logistics** - Account for accessibility and safety
6. **Plan for non-response** - Sample extras for expected attrition
7. **Archive sampling frames** - Save the full dataset used for sampling
