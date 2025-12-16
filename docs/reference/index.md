# API Reference

Comprehensive documentation of all modules, classes, and functions in the geo-sampling package.

## Core Modules

```{toctree}
:maxdepth: 2

extractor
sampler
visualization
data
cli
```

## Module Overview

### extractor
The `extractor` module handles downloading and processing OpenStreetMap data:
- Downloads administrative boundaries from GADM
- Fetches OSM road data from BBBike.org
- Processes and segments road shapefiles
- Outputs structured CSV files

### sampler
The `sampler` module implements various sampling strategies:
- Random sampling of road segments
- Stratified sampling by road type
- Filtering by road characteristics
- Geographic weighting options

### visualization
The `visualization` module provides plotting utilities:
- Map visualization functions
- Sample distribution plots
- Road network visualization
- Export to various formats

### data
The `data` module contains data access utilities:
- GADM boundary data access
- OSM data fetching and processing
- Data validation and cleaning

### cli
The `cli` module implements the command-line interface:
- Main entry point for the package
- Argument parsing and validation
- Workflow orchestration
- Progress reporting