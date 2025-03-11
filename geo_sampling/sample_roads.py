#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This module samples road segments from an input file and optionally plots them.
"""

import sys
import argparse
import csv
import random
from geo_sampling.utils import plot_road_segments, write_csv


def main(argv=None):
    """Main function to parse arguments and sample road segments."""
    if argv is None:
        argv = sys.argv[1:]

    parser = argparse.ArgumentParser(
        description="Randomly sample road segments"
    )
    parser.add_argument(
        "input", help="Road segments input file"
    )
    parser.add_argument(
        "-n", "--n-samples", dest="samples", type=int, default=0,
        help="Number of random samples"
    )
    parser.add_argument(
        "-t", "--types", nargs="+", dest="types", default=None,
        help="Select road types (list)"
    )
    parser.add_argument(
        "-o", "--output", default="sample-output.csv",
        help="Sample output file name"
    )
    parser.add_argument(
        "--no-header", dest="noheader", action="store_true",
        help="Output without the header"
    )
    parser.add_argument(
        "--plot", dest="plot", action="store_true",
        help="Plot the output"
    )
    parser.add_argument(
        "-s", "--seed", dest="seed", type=int, default=0,
        help="Random seed"
    )

    args = parser.parse_args(argv)

    if args.seed != 0:
        random.seed(args.seed)

    road_types = args.types
    segments = []

    # Read CSV file
    with open(args.input, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for row in reader:
            if road_types is None or row["osm_type"] in road_types:
                segments.append(row)

    total_segments = len(segments)
    if total_segments < args.samples:
        print(f"Sample larger than population ({args.samples} > {total_segments})")
        sys.exit(-1)

    # Randomly sample segments
    sample_segments = (
        random.sample(segments, args.samples)
        if args.samples > 0
        else segments
    )

    # Write to CSV
    write_csv(args.output, sample_segments, args.noheader)

    # Plot if requested
    if args.plot:
        plot_road_segments(
            sample_segments,
            title=(
                f"Road Segments Sample (N = {args.samples} of "
                f"{total_segments})"
            )
        )

    return 0


if __name__ == "__main__":
    sys.exit(main())
