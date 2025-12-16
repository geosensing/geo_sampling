# Command Line Interface (CLI) Examples

The `geo-sampling` CLI provides powerful command-line tools for batch processing and integration into research workflows. All examples show actual working commands with real outputs.

## CLI Commands Overview

The CLI provides four main commands:

| Command | Purpose | Example |
|---------|---------|---------|
| `extract` | Extract road segments from a region | `geo-sampling extract "India" "NCT of Delhi"` |
| `sample` | Create samples from extracted roads | `geo-sampling sample roads.csv --sample-size 1000` |
| `workflow` | Complete extract + sample pipeline | `geo-sampling workflow "Singapore" "Central" -n 100` |
| `info` | Get region information | `geo-sampling info "Thailand" "Bangkok"` |

## Complete Working Examples

### Extract Command

Extract all roads from Delhi, India:

```bash
geo-sampling extract "India" "NCT of Delhi" --output delhi_roads.csv
```

Extract only major roads:

```bash
geo-sampling extract "India" "NCT of Delhi" \
    --road-types primary \
    --road-types secondary \
    --road-types trunk \
    --output delhi_major_roads.csv
```

**Python API Equivalent:**

```python
import geo_sampling as gs

extractor = gs.RoadExtractor("India", "NCT of Delhi")
roads = extractor.get_roads(road_types=["primary", "secondary", "trunk"])
extractor.save_csv("delhi_major_roads.csv", road_types=["primary", "secondary", "trunk"])
```

### Sample Command

Random sample of 1000 segments:

```bash
geo-sampling sample delhi_roads.csv \
    --sample-size 1000 \
    --strategy random \
    --output delhi_sample_1000.csv
```

Stratified sample maintaining road type proportions:

```bash
geo-sampling sample delhi_roads.csv \
    --sample-size 500 \
    --strategy stratified \
    --seed 42 \
    --output delhi_stratified_500.csv
```

Sample only specific road types:

```bash
geo-sampling sample delhi_roads.csv \
    --sample-size 200 \
    --road-types primary \
    --road-types secondary \
    --output delhi_primary_secondary.csv
```

**Python API Equivalent:**

```python
import geo_sampling as gs

# Load roads from CSV
roads = gs.load_segments_from_csv("delhi_roads.csv")
sampler = gs.RoadSampler(roads)

# Random sampling
sample = sampler.random_sample(1000, seed=42)
sampler.save_csv(sample, "delhi_sample_1000.csv")

# Stratified sampling
stratified = sampler.stratified_sample(500, seed=42)
sampler.save_csv(stratified, "delhi_stratified_500.csv")

# Filtered sampling
filtered = sampler.random_sample(200, road_types=["primary", "secondary"])
sampler.save_csv(filtered, "delhi_primary_secondary.csv")
```

### Workflow Command (Extract + Sample)

Complete workflow in one command:

```bash
geo-sampling workflow "Singapore" "Central" \
    --sample-size 100 \
    --strategy random \
    --output singapore_sample.csv
```

Workflow with visualization:

```bash
geo-sampling workflow "Singapore" "Central" \
    --sample-size 100 \
    --plot \
    --output singapore_sample.csv
```

**Python API Equivalent:**

```python
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

# Plot results
gs.plot_road_segments(sample, title="Singapore Road Sample")
```

### Info Command

Get road information for a region:

```bash
geo-sampling info "Thailand" "Bangkok"
```

Get info with custom admin level:

```bash
geo-sampling info "Thailand" "Bangkok" --admin-level 2
```

**Python API Equivalent:**

```python
import geo_sampling as gs

# Get road summary for a region
summary = gs.get_road_summary("Thailand", "Bangkok", admin_level=1)
print(f"Total segments: {summary['total_segments']:,}")
print(f"Road types: {summary['road_types']}")
print(f"Road type breakdown: {summary['road_type_counts']}")
```

## Advanced CLI Patterns

### Chaining Commands

Extract, then sample, then analyze:

```bash
# Step 1: Extract
geo-sampling extract "India" "NCT of Delhi" --output delhi.csv

# Step 2: Sample
geo-sampling sample delhi.csv --sample-size 1000 --output delhi_1k.csv

# Step 3: Get info
geo-sampling info "India" "NCT of Delhi"
```

### Batch Processing Script

Process multiple regions systematically:

```bash
#!/bin/bash
# Batch process multiple regions

COUNTRIES=("Singapore" "Thailand" "India")
REGIONS=("Central" "Trang" "NCT of Delhi")

for i in ${!COUNTRIES[@]}; do
    country=${COUNTRIES[$i]}
    region=${REGIONS[$i]}
    output="${country,,}_${region,,// /_}.csv"

    echo "Processing $country - $region..."
    geo-sampling workflow \
        "$country" \
        "$region" \
        --sample-size 500 \
        --output "$output" \
        --plot
done
```

### Complete Research Example

Research scenario: Sampling roads in multiple Thai provinces for field survey:

```bash
# Step 1: Extract roads from multiple provinces
geo-sampling extract "Thailand" "Trang" \
    --road-types primary \
    --road-types secondary \
    --road-types tertiary \
    --output trang_roads.csv

geo-sampling extract "Thailand" "Phuket" \
    --road-types primary \
    --road-types secondary \  
    --road-types tertiary \
    --output phuket_roads.csv

# Step 2: Sample from each province
geo-sampling sample trang_roads.csv \
    --sample-size 200 \
    --strategy stratified \
    --output trang_sample.csv

geo-sampling sample phuket_roads.csv \
    --sample-size 150 \
    --strategy stratified \
    --output phuket_sample.csv

# Step 3: Analyze the samples
geo-sampling info "Thailand" "Trang"
geo-sampling info "Thailand" "Phuket"
```

## Actual CLI Output Examples

Real command outputs are available for download:

**📁 Command Logs**: [commands_log.txt](../../examples/outputs/03_cli_usage/commands_log.txt)

**📁 Sample Outputs**: [CLI sample files](../../examples/outputs/03_cli_usage/sample_outputs/)

### Example Output Format

When you run the commands, you'll see output like:

```bash
$ geo-sampling workflow "Singapore" "Central" --sample-size 100

Running complete workflow for Central, Singapore...
Target sample size: 100
✓ Extracted 470 road segments in 2.3s
✓ Created sample of 100 segments
✓ Saved 100 segments to workflow_sample.csv

Sample summary:
  primary: 25 (25.0%)
  residential: 35 (35.0%)  
  secondary: 20 (20.0%)
  tertiary: 15 (15.0%)
  unclassified: 5 (5.0%)
```

## Integration with Research Workflows

### Make-based Workflow

Create a `Makefile` for reproducible research:

```makefile
# Makefile for road sampling research

# Variables
COUNTRY = Thailand
REGION = Bangkok
SAMPLE_SIZE = 500
OUTPUT_DIR = data/samples

# Targets
.PHONY: all extract sample analyze clean

all: $(OUTPUT_DIR)/$(REGION)_sample.csv

$(OUTPUT_DIR)/$(REGION)_roads.csv:
	mkdir -p $(OUTPUT_DIR)
	geo-sampling extract "$(COUNTRY)" "$(REGION)" \
		--output $@

$(OUTPUT_DIR)/$(REGION)_sample.csv: $(OUTPUT_DIR)/$(REGION)_roads.csv  
	geo-sampling sample $< \
		--sample-size $(SAMPLE_SIZE) \
		--strategy stratified \
		--seed 42 \
		--output $@

analyze: $(OUTPUT_DIR)/$(REGION)_sample.csv
	@echo "Sample analysis for $(REGION):"
	@wc -l $<
	@cut -d',' -f4 $< | sort | uniq -c

clean:
	rm -rf $(OUTPUT_DIR)
```

Run with: `make REGION=Bangkok SAMPLE_SIZE=1000`

### Docker Integration

Create reproducible sampling environment:

```dockerfile
FROM python:3.11-slim

# Install geo-sampling
RUN pip install geo-sampling

# Set up working directory
WORKDIR /workspace
COPY scripts/ ./scripts/

# Default command
CMD ["geo-sampling", "--help"]
```

Use with:

```bash
# Build image
docker build -t geo-sampling .

# Run sampling
docker run -v $(PWD)/data:/workspace/data geo-sampling \
    geo-sampling workflow "Singapore" "Central" \
        --sample-size 100 \
        --output /workspace/data/singapore_sample.csv
```

## CLI Help Reference

### Get Command Help

```bash
# Main help
geo-sampling --help

# Command-specific help  
geo-sampling extract --help
geo-sampling sample --help
geo-sampling workflow --help
geo-sampling info --help

# Check version
geo-sampling --version
```

### Common Options

- `--output, -o`: Specify output file name
- `--sample-size, -n`: Number of segments to sample
- `--strategy`: Sampling strategy (random, stratified)
- `--seed, -s`: Random seed for reproducibility
- `--plot`: Create visualization plot
- `--road-types, -t`: Filter by road types (can specify multiple)

## Next Steps

- 🐍 See [Python API Examples](python-api.md) for programmatic usage
- 🎯 Explore [Advanced Sampling](advanced.md) strategies  
- 📚 Check the [API Reference](../reference/index.md)
- 📁 Download [example outputs](../../examples/outputs/)

## Source Code

Complete CLI examples are available:
- [03_cli_usage.py](../../examples/03_cli_usage.py) - Demonstrates all CLI commands
- [CLI output samples](../../examples/outputs/03_cli_usage/) - Real command outputs