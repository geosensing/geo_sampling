#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Process geo roads data to sample road segments, generate BBBike extract links,
and optionally plot the output.

This script:
    - Downloads GADM boundaries if needed.
    - Downloads OSM data from BBBike.org.
    - Extracts road segments from a roads shapefile.
    - Splits long segments into chunks (default 500 m).
    - Writes output to a CSV file.
    - Optionally plots the segments.
"""

import sys
import re
import os
import argparse
import csv
import random
import time
import shutil
import zipfile
import urllib.parse
from functools import partial
import requests

from matplotlib import colors
import matplotlib.pyplot as plt

from bs4 import BeautifulSoup
import shapefile

import pyproj
import utm

from shapely.geometry import LineString, Polygon
from shapely.ops import transform, unary_union


# Constants
GADM_SHP_URL_FMT = (
    "https://geodata.ucdavis.edu/gadm/gadm4.1/shp/gadm41_{0}_shp.zip"
)
BBBIKE_MAX_POINTS = 300
BBBIKE_MAX_WAIT = 50


def check_length(line_obj):
    """
    Print the lengths of segments in a LineString and the total length.
    """
    total = 0.0
    previous = None
    for point in line_obj.coords:
        if previous is None:
            previous = point
        else:
            segment = LineString([previous, point])
            seg_length = segment.length
            print(seg_length)
            total += seg_length
            previous = point
    print(f"Total: {total}")


def output_to_file(writer, uid, osm_id, osm_name, osm_type, line_obj):
    """
    Write segments of a LineString to CSV.

    Args:
        writer (csv.DictWriter): CSV writer.
        uid (int): Current segment ID.
        osm_id: OSM identifier.
        osm_name: OSM name.
        osm_type: OSM type.
        line_obj (LineString): Shapely LineString object.

    Returns:
        int: Updated segment ID.
    """
    previous = None
    for point in line_obj.coords:
        if previous is None:
            previous = tuple(point)
        else:
            start_long, start_lat = tuple(previous)
            end_long, end_lat = tuple(point)
            writer.writerow({
                "segment_id": uid,
                "osm_id": osm_id,
                "osm_name": osm_name,
                "osm_type": osm_type,
                "start_lat": start_lat,
                "start_long": start_long,
                "end_lat": end_lat,
                "end_long": end_long,
            })
            uid += 1
            previous = point
    return uid


def gadm_get_country_list():
    """
    Retrieve a list of countries and codes from GADM.
    """
    resp = requests.get("https://gadm.org/download_country.html")
    countries = {}
    if resp.status_code == 200:
        soup = BeautifulSoup(resp.text, "html.parser")
        select_tag = soup.find("select", {"name": "country"})
        if select_tag:
            for opt in select_tag.find_all("option"):
                countries[opt.text.strip()] = opt["value"]
    return countries


def download_url(url, local_path):
    """
    Download a URL to a local file.

    Args:
        url (str): The URL to download.
        local_path (str): Path to save the file.
    """
    resp = requests.get(url, stream=True)
    with open(local_path, "wb") as out_file:
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                out_file.write(chunk)


def gadm_download_country_data(ccode):
    """
    Download GADM boundary data for a country.

    Args:
        ccode (str): Country code.

    Returns:
        str: Local filename of downloaded data.
    """
    url = GADM_SHP_URL_FMT.format(ccode)
    local_filename = os.path.join("data", url.rsplit('/', maxsplit=1)[-1])
    download_url(url, local_filename)
    return local_filename


def redistribute_vertices(geom, distance):
    """
    Redistribute vertices along a LineString to achieve approximately equal
    segments of a given distance.

    Args:
        geom (LineString): The original LineString.
        distance (float): Desired segment length in meters.

    Returns:
        LineString: New LineString with redistributed vertices.

    Raises:
        ValueError: If geometry type is unhandled.
    """
    if geom.geom_type == "LineString":
        num_vertices = int(round(geom.length / distance))
        num_div = geom.length / distance
        if num_vertices == 0:
            num_vertices = 1
        new_points = [
            geom.interpolate(float(i) / num_div, normalized=True)
            for i in range(num_vertices)
        ]
        new_points.append(geom.interpolate(1, normalized=True))
        return LineString(new_points)
    if geom.geom_type == "MultiLineString":
        parts = [redistribute_vertices(part, distance) for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])

    raise ValueError(f"Unhandled geometry {geom.geom_type}")


def bbbike_generate_extract_link(args):
    """
    Generate a BBBike extract URL for a specified administrative boundary.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        tuple: (city, URL) if successful; otherwise (None, None).
    """
    shp_file = f"data/gadm41_{args.ccode}_{args.level}.shp"
    if not os.path.exists(shp_file):
        print(f"No boundary data at this level (level={args.level})")
        return None, None

    levels_engtype = []
    levels_type = []
    names_idx = []
    nl_names_idx = []
    names = []
    nl_names = []
    for level in range(1, args.level + 1):
        shp_path = f"data/gadm41_{args.ccode}_{level}.shp"
        dbf_path = f"data/gadm41_{args.ccode}_{level}.dbf"
        with open(shp_path, "rb") as shp, open(dbf_path, "rb") as dbf:
            reader = shapefile.Reader(shp=shp, dbf=dbf)
            shape_records = reader.shapeRecords()
            idx = 0
            engtype_idx = None
            type_idx = None
            name_idx = None
            nl_name_idx = None

            for field in reader.fields:
                if isinstance(field, list):
                    if field[0] == f"ENGTYPE_{level}":
                        engtype_idx = idx
                    if field[0] == f"TYPE_{level}":
                        type_idx = idx
                    if field[0] == f"NAME_{level}":
                        name_idx = idx
                    if field[0] == f"NL_NAME_{level}":
                        nl_name_idx = idx
                    idx += 1
            if shape_records:
                levels_engtype.append(shape_records[0].record[engtype_idx])
                levels_type.append(shape_records[0].record[type_idx])
                names_idx.append(name_idx)
                nl_names_idx.append(nl_name_idx)
            if level == args.level:
                for rec_obj in shape_records:
                    name_val = "+".join([rec_obj.record[i] for i in names_idx])
                    names.append(name_val)
                    nl_name_val = "+".join([rec_obj.record[i] for i in nl_names_idx])
                    nl_names.append(nl_name_val)
    if args.name not in names:
        print("All region names :-")
        for name in names:
            try:
                print(f"- {name}")
            except Exception:  # pylint: disable=broad-except
                print(f"- {name}")
        return None, None
    for rec_obj in shape_records:
        name_val = "+".join([rec_obj.record[i] for i in names_idx])
        if args.name == name_val:
            points = []
            parts = []
            part_start = 0
            for part in rec_obj.shape.parts:
                if part != 0:
                    parts.append(rec_obj.shape.points[part_start:part])
                    part_start = part
            parts.append(rec_obj.shape.points[part_start:])
            polygon_list = []
            max_area = 0
            max_polygon = None
            for line_points in parts:
                poly = Polygon(line_points)
                area = poly.area
                if area > max_area:
                    max_area = area
                    max_polygon = poly
                polygon_list.append(poly)
            extra_polygons = []
            for poly in polygon_list:
                if poly != max_polygon:
                    connecting_line = LineString(
                        [poly.centroid, max_polygon.centroid]
                    )
                    extra_polygons.append(connecting_line.buffer(0.00001))
            polygon_list.extend(extra_polygons)
            union_poly = unary_union(polygon_list)
            boundary_line = LineString(union_poly.exterior.coords)
            new_length = boundary_line.length / BBBIKE_MAX_POINTS
            new_line = redistribute_vertices(boundary_line, new_length)
            for lat, lng in new_line.coords:
                points.append(f"{lat:.3f},{lng:.3f}")
            coords = "|".join(points)
            sw_lng, sw_lat, ne_lng, ne_lat = rec_obj.shape.bbox
            city = f"{args.ccode}_{args.name}"
            extract_format = "shp.zip"
            params = {
                "city": city,
                "coords": coords,
                "format": extract_format,
                "sw_lat": sw_lat,
                "sw_lng": sw_lng,
                "ne_lat": ne_lat,
                "ne_lng": ne_lng,
                "email": "geo_sampling@mailinator.com",
                "as": 1,
                "pg": 0,
            }
            encoded_params = urllib.parse.urlencode(params)
            base_url = "https://extract.bbbike.org/?"
            url = base_url + encoded_params
            file_name = f"bbbike_{args.ccode}_{args.name}.txt"
            with open(file_name, "w", encoding="utf-8") as out_file:
                out_file.write(url)
            return city, url


def bbbike_submit_extract_link(args):
    """
    Submit the extract link to BBBike.org.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        bool: True if submission is successful, False otherwise.
    """
    response = requests.get(args.bbbike_url + "&submit=1")
    if response.status_code == 200:
        print("Extract link submitted")
        return True
    return False


def bbbike_check_download_link(args):
    """
    Check for the download link on BBBike.org until it is ready or times out.

    Args:
        args (argparse.Namespace): Parsed command-line arguments.

    Returns:
        str: The download link if found; otherwise an empty string.
    """
    wait_time = 0
    while wait_time < BBBIKE_MAX_WAIT:
        try:
            response = requests.get("https://download.bbbike.org/osm/extract/?date=all")
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, "html.parser")
                city_span = soup.find("span", {"title": args.city})
                if city_span:
                    siblings = city_span.parent.find_next_siblings()
                    if len(siblings) >= 3:
                        dl_section = siblings[2]
                        link_tag = dl_section.find("a")
                        if link_tag:
                            href = link_tag["href"]
                            return "https://download.bbbike.org/" + href
            print("Waiting for download link ready (15s)...")
            time.sleep(15)
        except KeyboardInterrupt as err:
            print(err)
            break
        wait_time += 1
    print("Cannot get download link from BBBike.org")
    return ""




def main(argv=None):
    """
    Main function for processing geo roads data and generating BBBike extract links.

    Args:
        argv (list): Command-line arguments.

    Returns:
        int: Exit code.
    """
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(description="Geo roads data")
    parser.add_argument(
        "-c", "--country", dest="country", default=None,
        help="Select country"
    )
    parser.add_argument(
        "-l", "--level", dest="level", default=1, type=int,
        choices=list(range(1, 5)), help="Select administrative level"
    )
    parser.add_argument(
        "-n", "--name", dest="name", default=None,
        help="Select region name"
    )
    parser.add_argument(
        "-t", "--types", nargs="+", dest="types", default=None,
        help="Select road types (list)"
    )
    parser.add_argument(
        "-o", "--output", default="output.csv",
        help="Output file name"
    )
    parser.add_argument(
        "-d", "--distance", dest="distance", type=int, default=500,
        help="Distance in meters to split"
    )
    parser.add_argument(
        "--no-header", dest="noheader", action="store_true",
        help="Output without the header"
    )
    parser.set_defaults(noheader=False)
    parser.add_argument(
        "--plot", dest="plot", action="store_true",
        help="Plot the output"
    )
    parser.set_defaults(plot=False)

    args = parser.parse_args(argv)
    print(args)

    countries = gadm_get_country_list()
    if args.country not in list(countries.keys()):
        print("All country list :-")
        for country in sorted(countries.keys()):
            print(f"- {country}")  # Fixed: using f-string
        print("Please specify a country name from above list with -c option.")
        sys.exit(-1)

    if not os.path.exists("data"):
        os.makedirs("data")

    args.ccode = countries[args.country].split("_")[0]
    gadm_shp_file = f"data/gadm41_{args.ccode}_shp.zip"  # Fixed: using f-string
    if os.path.exists(gadm_shp_file):
        print("Using exists administrative boundary data file...")
    else:
        print("Download administrative boundary data file...")
        gadm_shp_file = gadm_download_country_data(args.ccode)

    with zipfile.ZipFile(gadm_shp_file, "r") as zip_file:
        for file in zip_file.namelist():
            for level in range(1, args.level + 1):
                pattern = fr".*_{args.ccode}_{level}\.(:?dbf|shp)"
                if re.match(pattern, file):
                    zip_file.extract(file, "data")

    print("Boundary data extracted.")

    osm_shape_filename = f"data/{args.ccode}_{args.name}_osm.shp.zip"  # Fixed: using f-string
    if os.path.exists(osm_shape_filename):
        print("Using exists OSM data file...")
    else:
        print("Create BBBike.org data extract URL...")
        args.city, args.bbbike_url = bbbike_generate_extract_link(args)
        if args.city is None:
            print("Please specify a region name from above list with -n option.")
            sys.exit(-2)
        print("Submit data extract URL to BBBike.org...")
        if bbbike_submit_extract_link(args):
            url = bbbike_check_download_link(args)
            print("Download extracted OSM data files...")
            download_url(url, osm_shape_filename)

    print("Extract OSM data file (Roads shapefile)...")
    zip_file = zipfile.ZipFile(osm_shape_filename, 'r')
    for file in zip_file.namelist():
        fn = os.path.basename(file)
        if re.match('roads.(:?dbf|shp)', fn):
            # copy file (taken from zipfile's extract)
            source = zip_file.open(file)
            target = open(os.path.join('data',
                          args.ccode + '_' + args.name + '_' + fn), "wb")
            with source, target:
                shutil.copyfileobj(source, target)
    zip_file.close()

    shp_path = f"data/{args.ccode}_{args.name}_roads.shp"  # Fixed: using f-string
    dbf_path = f"data/{args.ccode}_{args.name}_roads.dbf"  # Fixed: using f-string
    with open(shp_path, "rb") as shp_file, open(dbf_path, "rb") as dbf_file:
        reader = shapefile.Reader(shp=shp_file, dbf=dbf_file)
        shape_records = reader.shapeRecords()

    type_index = 3
    road_types_set = set()
    for record in shape_records:
        road_types_set.add(record.record[type_index])
    print("All road types :-")
    for road_type in road_types_set:
        selected = True if args.types is None else (road_type in args.types)
        print(f"{('*' if selected else '-')} {road_type}")  # Fixed: using f-string
    print("You can specify the road types with -t. (* is selected)")

    # Determine UTM zone for coordinate transformation
    lng, lat = shape_records[0].shape.points[0]
    _, _, zone_x, _ = utm.from_latlon(lat, lng)

    # Define the coordinate reference systems
    wgs84 = pyproj.CRS.from_epsg(4326)  # WGS84
    utm_crs = pyproj.CRS.from_proj4(f"+proj=utm +zone={zone_x} +datum=WGS84 +units=m +no_defs")

    # Create transformer objects
    wgs_to_utm_transformer = pyproj.Transformer.from_crs(wgs84, utm_crs, always_xy=True).transform
    utm_to_wgs_transformer = pyproj.Transformer.from_crs(utm_crs, wgs84, always_xy=True).transform

    # Use partial to make the functions similar to the old code
    wgs_to_utm = partial(wgs_to_utm_transformer)
    utm_to_wgs = partial(utm_to_wgs_transformer)

    uid = 0
    selected_road_types = args.types

    if args.plot:
        c_values = list(colors.cnames.values())
        road_colors = selected_road_types if selected_road_types else []
        fig, axis = plt.subplots(figsize=(14, 10))
        first = []

    with open(args.output, "w", newline="", encoding="utf-8") as output_file:
        cols = [
            "segment_id", "osm_id", "osm_name", "osm_type", "start_lat",
            "start_long", "end_lat", "end_long"
        ]
        writer = csv.DictWriter(output_file, fieldnames=cols)
        if not args.noheader:
            writer.writeheader()

        for record in shape_records:
            rec = record.record
            road_type_value = rec[type_index]
            if selected_road_types is None or road_type_value in selected_road_types:
                points = record.shape.points
                line = LineString(points)
                new_line = transform(wgs_to_utm, line)
                segments_line = redistribute_vertices(new_line, args.distance)
                osm_id = rec[0]
                osm_name = rec[1].strip() if rec[1] else ""
                osm_type = rec[3].strip() if rec[3] else ""
                new_segments = transform(utm_to_wgs, segments_line)
                uid = output_to_file(
                    writer, uid, osm_id, osm_name, osm_type, new_segments
                )
                if args.plot:
                    p_coords = new_segments.coords
                    x_coords = [pt[0] for pt in p_coords]
                    y_coords = [pt[1] for pt in p_coords]
                    if road_type_value not in road_colors:
                        road_colors.append(road_type_value)
                    color_val = c_values[road_colors.index(road_type_value) %
                                           len(c_values)]
                    if road_type_value not in first:
                        first.append(road_type_value)
                        axis.plot(x_coords, y_coords, color=color_val,
                                  label=road_type_value)
                    else:
                        axis.plot(x_coords, y_coords, color=color_val)

    if args.plot:
        axis.get_yaxis().get_major_formatter().set_useOffset(False)
        axis.get_yaxis().get_major_formatter().set_scientific(False)
        axis.get_xaxis().get_major_formatter().set_useOffset(False)
        axis.get_xaxis().get_major_formatter().set_scientific(False)
        plt.legend(loc="best", fancybox=True, framealpha=0.5)
        plt.title(f"{args.name}, {args.country}")  # Fixed: using f-string
        plt.show()

    print("Done")
    return 0

if __name__ == "__main__":
    sys.exit(main())
