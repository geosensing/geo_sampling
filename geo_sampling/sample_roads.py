#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import argparse
import csv
import random


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Random sample road segments')
    parser.add_argument('input', default=None,
                        help='Road segments input file')
    parser.add_argument('-n', '--n-samples', dest='samples', type=int,
                        default=0, help='Number of random samples')
    parser.add_argument('-t', '--types', nargs='+', dest='types',
                        default=None, help='Select road types (list)')
    parser.add_argument('-o', '--output', default='sample-output.csv',
                        help='Sample output file name')
    parser.add_argument('--no-header', dest='noheader', action='store_true',
                        help='Output without header at the first row')
    parser.set_defaults(noheader=False)
    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)

    args = parser.parse_args(argv)

    print(args)

    road_types = args.types

    if args.plot:
        # Delay import
        try:
            from matplotlib import colors
            import matplotlib.pyplot as plt

            cvalues = colors.cnames.values()
            road_colors = road_types if road_types else []
            fig, ax = plt.subplots(figsize=[14, 10])
            first = []
        except ImportError as e:
            print("WARNING matplotlib is not installed")
            args.plot = False

    segments = []
    with open(args.input) as f:
        reader = csv.DictReader(f)
        for r in reader:
            if road_types is None or r['osm_type'] in road_types:
                segments.append(r)

    total = len(segments)

    if total < args.samples:
        print("Sample larger than population ({0} > {1})".format(args.samples,
                                                                 total))
        sys.exit(-1)

    if args.samples == 0:
        args.samples = total
        sample_segments = segments
    else:
        sample_segments = [segments[i] for i in
                           sorted(random.sample(xrange(len(segments)),
                                                args.samples))]

    with open(args.output, 'wb') as f:
        cols = ['segment_id', 'osm_id', 'osm_name', 'osm_type', 'start_lat',
                'start_long', 'end_lat', 'end_long']
        writer = csv.DictWriter(f, fieldnames=cols)
        if not args.noheader:
            writer.writeheader()

        for s in sample_segments:
            t = s['osm_type']
            if road_types is None or t in road_types:
                writer.writerow(s)
                if args.plot:
                    x = [s['start_long'], s['end_long']]
                    y = [s['start_lat'], s['end_lat']]
                    if t not in road_colors:
                        road_colors.append(t)
                    c = cvalues[road_colors.index(t) % len(cvalues)]
                    if t not in first:
                        first.append(t)
                        ax.plot(x, y, color=c, label=t)
                    else:
                        ax.plot(x, y, color=c)

    if args.plot:
        plt.legend(loc='best', fancybox=True, framealpha=0.5)
        plt.title('Road segments random sample (N = {0} of {1})'
                  .format(args.samples, total))
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)
        plt.show()

    return 0


if __name__ == "__main__":
    sys.exit(main())
