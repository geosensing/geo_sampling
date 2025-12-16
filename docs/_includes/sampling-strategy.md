# Sampling Strategy

This package implements a systematic approach to sampling street locations for data collection. The strategy ensures representative coverage of road networks for research purposes.

## 1. Sampling Frame

Get all the streets in the region of interest from [OpenStreetMap](https://www.openstreetmap.org/). The package:

1. Downloads administrative boundary data from [GADM](http://www.gadm.org/) in ESRI format
2. Identifies the geographic bounds of your region of interest
3. Extracts road data from [BBBike.org](http://extract.bbbike.org) for the bounded area
4. Processes the road network into manageable segments

Administrative levels are hierarchical - cities are nested in states, which are nested in countries. You can sample at any administrative level depending on your research needs.

## 2. Sampling Design

### Road Segmentation
- Each street is split into **500-meter segments** from end to end
- Shorter streets (< 500m) remain as single segments
- Each segment is treated as a straight line between start and end points
- Segments maintain OpenStreetMap metadata (road type, name, ID)

### Road Type Classification
The package preserves OpenStreetMap road classifications:
- **trunk**: National highways and major arterials
- **primary**: Major roads connecting cities/towns
- **secondary**: Important roads for regional traffic
- **tertiary**: Roads connecting smaller settlements
- **residential**: Roads in residential areas
- **unclassified**: Minor public roads
- **service**: Access roads to buildings/areas

### Sampling Methods
- **Random sampling**: Equal probability selection across all segments
- **Stratified sampling**: Maintains proportional representation of road types
- **Filtered sampling**: Restricts sampling to specific road types
- **Length-based sampling**: Target specific total coverage distances

## 3. Data Collection Framework

The output provides GPS coordinates and metadata for each sampled segment:

- **Start/end coordinates**: Precise lat/long boundaries for data collection
- **Road metadata**: Type, name, and OpenStreetMap ID for context
- **Segment ID**: Unique identifier for tracking and quality control

These coordinates define the geographic areas where field data collection should occur, ensuring systematic coverage of the road network.
