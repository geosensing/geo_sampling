# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Python package for geographic road sampling that enables random sampling of street locations for data collection purposes. The core workflow involves downloading OpenStreetMap data, processing road segments, and generating sampling coordinates for field research.

## Key Architecture

The package consists of three main modules:

- **geo_roads.py**: Downloads GADM administrative boundaries and OSM data from BBBike.org, processes road shapefiles, splits long segments into 500m chunks, and outputs CSV data. Provides the `geo_roads` CLI command.
- **sample_roads.py**: Takes processed road data and randomly samples segments based on specified criteria (road types, sample size). Provides the `sample_roads` CLI command.  
- **utils.py**: Contains plotting and CSV writing utilities shared across modules.

## Development Commands

### Testing
```bash
pytest                    # Run all tests
python -m unittest tests.test_010_geo_roads  # Run geo_roads tests
python -m unittest tests.test_020_sample_roads  # Run sample_roads tests
python -m unittest discover tests  # Alternative way to run all tests
```

### Linting and Code Quality
```bash
flake8 .                  # Style checking (used in CI)
pylint $(git ls-files '*.py')  # Static analysis (used in CI)
```

### Package Building
```bash
pip install -e .          # Install in development mode
python -m build           # Build distribution packages
pip install .             # Install package normally
```

### Documentation
```bash
cd docs && make html      # Build Sphinx documentation
cd docs && make clean     # Clean documentation build
```

## CLI Commands

The package provides two main CLI commands installed via setuptools entry points:

- `geo_roads`: Process geographic regions to extract road segments
- `sample_roads`: Sample from processed road segments

Environment variables for testing:
- `COUNTRY_NAME`: Country for test data (default: Singapore)
- `REGION_NAME`: Region within country (default: North)  
- `ADM_LEVEL`: Administrative level (default: 1)

## Data Flow

1. **geo_roads** downloads GADM boundaries → fetches OSM data from BBBike → processes road shapefiles → outputs segmented road CSV
2. **sample_roads** reads road CSV → applies filtering/sampling criteria → outputs sampled segments CSV
3. Optional plotting functionality visualizes sampled segments by road type

## Implementation Notes

- Tests use environment variables for configuration (COUNTRY_NAME, REGION_NAME, ADM_LEVEL)
- BBBike.org extract URLs are dynamically generated via web scraping
- Road segments are split into 500m chunks for consistent sampling density
- Geographic transformations use UTM coordinate system for distance calculations
- CI runs on Python 3.11 with flake8 and pylint for code quality

## Dependencies

Core dependencies include pyshp (shapefile processing), matplotlib (plotting), pyproj/utm (coordinate transformations), Shapely (geometry operations), and beautifulsoup4/requests (web scraping BBBike extract URLs).