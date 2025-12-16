# Quick Start

Get started with geo-sampling in 5 minutes! This guide shows you how to extract and sample road segments using both the command-line interface and Python API.

## Command-Line Interface (CLI)

### Complete Workflow in One Command

Extract roads and create a sample for Singapore in a single command:

```bash
geo-sampling workflow "Singapore" "Central" \
    --sample-size 100 \
    --output singapore_sample.csv \
    --plot
```

### Step-by-Step Approach

For more control, use the step-by-step approach:

```bash
# 1. Extract all roads
geo-sampling extract "India" "NCT of Delhi" \
    --output delhi_roads.csv

# 2. Create a random sample
geo-sampling sample delhi_roads.csv \
    --sample-size 1000 \
    --strategy random \
    --output delhi_sample.csv \
    --plot

# 3. Get information about a region
geo-sampling info "Thailand" "Bangkok"
```

## Python API

### One-Liner Convenience Function

```python
import geo_sampling as gs

# Quick sampling for research
sample = gs.sample_roads_for_region(
    "Singapore", "Central", 
    n=100, 
    strategy="random",
    seed=42
)

# Plot the results
gs.quick_plot(sample, title="Singapore Road Sample")
```

### Step-by-Step with Full Control

```python
import geo_sampling as gs

# Extract roads from a region
extractor = gs.RoadExtractor("India", "NCT of Delhi")
roads = extractor.get_roads(road_types=["primary", "secondary"])

# Create sampler and generate sample
sampler = gs.RoadSampler(roads)
sample = sampler.random_sample(1000, seed=42)

# Save and visualize
sampler.save_csv(sample, "delhi_sample.csv")
gs.plot_road_segments(sample, title="Delhi Road Sample")
```

## What's Next?

- 📖 Check out [detailed examples](examples/index.md) for more complex use cases
- 🔧 Learn about [advanced sampling strategies](examples/advanced.md)  
- 📚 Browse the [API reference](reference/index.md) for complete documentation