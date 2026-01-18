# Geo sampling: Randomly sample locations on streets

[![CI](https://github.com/geosensing/geo-sampling/actions/workflows/ci.yml/badge.svg)](https://github.com/geosensing/geo-sampling/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/geo_sampling.svg?maxAge=3600)](https://pypi.python.org/pypi/geo_sampling)
[![Documentation](https://img.shields.io/badge/docs-GitHub%20Pages-blue)](https://geosensing.github.io/geo-sampling/)
[![Downloads](https://pepy.tech/badge/geo-sampling)](https://pepy.tech/project/geo-sampling)

Say you want to learn about the average number of potholes per kilometer of street in a city. Or estimate a similar such quantity. To estimate the quantity, you need to sample locations on the streets. This package helps you sample those locations. In particular, the package implements the following sampling strategy:

## Sampling Strategy

### 1. Sampling Frame
Get all the streets in the region of interest from [OpenStreetMap](https://www.openstreetmap.org/#map=5/51.500/-0.100). To accomplish that, the package first downloads administrative boundary data for the country in which the region is located in ESRI format from http://www.gadm.org/country. The administrative data is in multiple levels, for instance, cities are nested in states, which are nested in countries. The user can choose a city or state, but not a portion of a city. And then the package uses the [pyshp package](https://pypi.python.org/pypi/pyshp) to build a URL for the site http://extract.bbbike.org from which we can download the OSM data.

### 2. Sampling Design

* For each street (or road), starting from one end of the street, we split the street into .5 km segments till we reach the end of the street. (The last segment, or if the street is shorter than .5km, the only segment, can be shorter than .5 km.)

* Get the lat/long of starting and ending points of each of the segments. And assume that the street is a straight line between the .5 km segment.

* Next, create a database of all the segments

* Sample rows from the database and produce a CSV of the sampled segments

* Plot the lat/long --- filling all the area within the segment. These shaded regions are regions for which data needs to be collected.

### 3. Data Collection
Collect data on the highlighted segments.

## Installation

### Prerequisites

The package requires Python 3.11 or higher. Install the package from PyPI:

```bash
pip install geo-sampling
```

### Development Installation

For development, install with development dependencies:

```bash
git clone https://github.com/geosensing/geo-sampling.git
cd geo-sampling
uv sync --group dev
```

#### Pre-commit Hooks

To ensure code quality, install pre-commit hooks:

```bash
uv run pre-commit install
```

This will automatically run linting, formatting, and type checking before each commit. You can also run the hooks manually:

```bash
uv run pre-commit run --all-files
```

## Quick Start

### Command Line Interface

Complete workflow in one command:

```bash
# Install the package
pip install geo-sampling

# Sample 100 road segments from Singapore
geo-sampling workflow "Singapore" "Central" \
    --sample-size 100 \
    --output singapore_sample.csv \
    --plot
```

### Python API

```python
import geo_sampling as gs

# Quick sampling for research
sample = gs.sample_roads_for_region(
    "Singapore", "Central",
    n=100,
    strategy="random"
)

# Plot and save
gs.quick_plot(sample, title="Singapore Sample")
sampler = gs.RoadSampler(sample)
sampler.save_csv(sample, "singapore_sample.csv")
```

## Documentation

📖 **[Complete Documentation](https://geosensing.github.io/geo-sampling/)** - Comprehensive guides and examples

🚀 **[Quick Start Guide](https://geosensing.github.io/geo-sampling/quickstart.html)** - Get up and running in 5 minutes

🐍 **[Python API Examples](https://geosensing.github.io/geo-sampling/examples/python-api.html)** - Complete code examples with real data

💻 **[CLI Usage Guide](https://geosensing.github.io/geo-sampling/examples/cli-usage.html)** - Command-line interface examples

📁 **[Example Outputs](examples/outputs/)** - Download real sample data and plots

## 🔗 Adjacent Repositories

- [geosensing/latlong-to-zip](https://github.com/geosensing/latlong-to-zip) — Reverse Geocode Lat/Long to Zip Codes using GeoNames, AskGeo, or Google. Compare Geocoding Services.
- [geosensing/autosense](https://github.com/geosensing/autosense) — AutoSense: Automated Street Condition Assessment
- [geosensing/streetsense](https://github.com/geosensing/streetsense) — Street Sense: Learning from Google Street View
- [geosensing/women-count](https://github.com/geosensing/women-count) — Missing Women on the streets of Delhi
- [geosensing/ybar](https://github.com/geosensing/ybar) — Web application for mobile phones to crowdsource data collection from geographically distributed locations
## Authors

Suriyan Laohaprapanon and Gaurav Sood

## License

Scripts are released under the [MIT License](LICENSE).
