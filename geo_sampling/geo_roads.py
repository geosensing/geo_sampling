#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import re
import os
import argparse
import csv
import requests
from bs4 import BeautifulSoup
import zipfile
import urllib
import time
import shutil

import shapefile  # https://pypi.python.org/pypi/pyshp
from shapely.geometry import LineString, Polygon
from functools import partial
import pyproj
from shapely.ops import transform, cascaded_union
import utm

GADM_SHP_URL_FMT = 'http://biogeo.ucdavis.edu/data/gadm2.8/shp/{0}_adm_shp.zip'

# To workaround request entity too large in URL request
BBBIKE_MAX_POINTS = 300
BBBIKE_MAX_WAIT = 50


def check_length(l):
    total = 0.0
    prev = None
    for p in l.coords:
        if prev is None:
            prev = p
        else:
            line = LineString([prev, p])
            prev = p
            l = line.length
            print(l)
            total += l
    print("Total: {0}".format(total))


def output_to_file(writer, uid, osm_id, osm_name, osm_type, l):
    prev = None
    for p in l.coords:
        if prev is None:
            prev = p
        else:
            start_long, start_lat = prev
            end_long, end_lat = p
            writer.writerow({'segment_id': uid, 'osm_id': osm_id,
                             'osm_name': osm_name, 'osm_type': osm_type,
                             'start_lat': start_lat, 'start_long': start_long,
                             'end_lat': end_lat, 'end_long': end_long})
            uid += 1
            prev = p
    return uid


def gadm_get_country_list():
    r = requests.get('http://gadm.org/country')
    countries = {}
    if r.status_code == 200:
        soup = BeautifulSoup(r.text, 'html.parser')
        for opt in soup.find('select', {'name': 'cnt'}).find_all('option'):
            countries[opt.text.strip()] = opt['value']
    return countries


def download_url(url, local):
    # NOTE the stream=True parameter
    r = requests.get(url, stream=True)
    with open(local, 'wb') as f:
        for chunk in r.iter_content(chunk_size=1024):
            if chunk:  # filter out keep-alive new chunks
                f.write(chunk)


def gadm_download_country_data(ccode):
    url = GADM_SHP_URL_FMT.format(ccode)
    local_filename = 'data/' + url.split('/')[-1]
    download_url(url, local_filename)
    return local_filename


def redistribute_vertices(geom, distance):
    if geom.geom_type == 'LineString':
        num_vert = int(round(geom.length / distance))
        num_vert_div = geom.length / distance
        if num_vert == 0:
            num_vert = 1
        return LineString(
            [geom.interpolate(float(n) / num_vert_div, normalized=True)
             for n in range(num_vert)] +
            [geom.interpolate(1, normalized=True)])

    elif geom.geom_type == 'MultiLineString':
        parts = [redistribute_vertices(part, distance)
                 for part in geom]
        return type(geom)([p for p in parts if not p.is_empty])
    else:
        raise ValueError('unhandled geometry %s', (geom.geom_type,))


def bbbike_generate_extract_link(args):
    if not os.path.exists('data/{0}_adm{1}.shp'
                          .format(args.ccode, args.level)):
        print("No boundary data at this level (level={0})".format(args.level))
        return None, None

    levels_type = []
    levels_engtype = []
    names_idx = []
    nl_names_idx = []
    names = []
    nl_names = []
    for l in range(1, args.level + 1):
        shp = open('data/{0}_adm{1}.shp'.format(args.ccode, l), 'rb')
        dbf = open('data/{0}_adm{1}.dbf'.format(args.ccode, l), 'rb')

        reader = shapefile.Reader(shp=shp, dbf=dbf)
        sr = reader.shapeRecords()
        idx = 0
        for f in reader.fields:
            if type(f) == list:
                if f[0] == 'ENGTYPE_{0:d}'.format(l):
                    engtype_idx = idx
                if f[0] == 'TYPE_{0:d}'.format(l):
                    type_idx = idx
                if f[0] == 'NAME_{0:d}'.format(l):
                    name_idx = idx
                if f[0] == 'NL_NAME_{0:d}'.format(l):
                    nl_name_idx = idx
                idx += 1
        if len(sr):
            levels_engtype.append(sr[0].record[engtype_idx])
            levels_type.append(sr[0].record[type_idx])
            names_idx.append(name_idx)
            nl_names_idx.append(nl_name_idx)
        if l == args.level:
            for s in sr:
                name = '+'.join([s.record[i] for i in names_idx])
                names.append(name)
                nl_name = '+'.join([s.record[i] for i in nl_names_idx])
                nl_names.append(nl_name)

    if args.name not in names:
        print("All region names :-")
        for n in names:
            try:
                print("- {0}".format(n.encode('utf-8')))
            except:
                print("- {0}".format(n))
        return None, None

    for s in sr:
        name = '+'.join([s.record[i] for i in names_idx])
        if args.name == name:
            points = []
            # Split boundary line for each parts
            lines = []
            pp = 0
            for p in s.shape.parts:
                if p != 0:
                    lines.append(s.shape.points[pp:p])
                    pp = p
            lines.append(s.shape.points[p:])
            pg_list = []
            # Find maximum area part
            ma = 0
            mp = None
            for l in lines:
                pg = Polygon(l)
                a = pg.area
                if a > ma:
                    ma = a
                    mp = pg
                pg_list.append(pg)
            # Create extra polygon to connect all multi-parts boundary
            x_pg_list = []
            for p in pg_list:
                if p != mp:
                    line = LineString([p.centroid, mp.centroid])
                    x_pg_list.append(line.buffer(0.00001))
            pg_list.extend(x_pg_list)
            new_pg_list = cascaded_union(pg_list)
            line = LineString(new_pg_list.exterior.coords)
            # Simplify boundary line to workaround
            # Request entity too large due to too long URL request.
            new_len = line.length / BBBIKE_MAX_POINTS
            new_line = redistribute_vertices(line, new_len)
            for lat, lng in new_line.coords:
                points.append('%.3f,%.3f' % (lat, lng))
            coords = '|'.join(points)
            sw_lng, sw_lat, ne_lng, ne_lat = s.shape.bbox
            city = args.ccode + '_' + args.name
            fmt = 'shp.zip'
            params = {'city': city, 'coords': coords, 'format': fmt,
                      'sw_lat': sw_lat, 'sw_lng': sw_lng, 'ne_lat': ne_lat,
                      'ne_lng': ne_lng, 'email': 'geo_sampling@mailinator.com',
                      'as': 1, 'pg': 0}
            encoded_params = urllib.urlencode(params)
            base_url = 'http://extract.bbbike.org/?'
            url = base_url + encoded_params
            # Save BBBike data extract URL for debug
            fn = 'bbbike_{0}_{1}.txt'.format(args.ccode, args.name)
            with open(fn, 'wb') as f:
                f.write(url)
            return city, url


def bbbike_submit_extract_link(args):
    r = requests.get(args.bbbike_url + "&submit=1")
    if r.status_code == 200:
        print("Extract link submitted")
        return True
    else:
        return False


def bbbike_check_download_link(args):
    wait = 0
    while wait < BBBIKE_MAX_WAIT:
        try:
            r = requests.get('http://download.bbbike.org/osm/extract/?date=all')
            if r.status_code == 200:
                soup = BeautifulSoup(r.text, 'html.parser')
                city_span = soup.find('span', {'title': args.city})
                if city_span:
                    dl = city_span.parent.find_next_siblings()[2]
                    link = dl.find('a')
                    if link:
                        href = link['href']
                        return 'http://download.bbbike.org/' + href
            print("Waiting for download link ready (15s)...")
            time.sleep(15)
        except KeyboardInterrupt as e:
            print(e)
            break
        wait += 1
    print("Cannot get download link from BBBike.org")
    return ''


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser(description='Geo roads data')
    parser.add_argument('-c', '--country', dest='country', default=None,
                        help='Select country')
    parser.add_argument('-l', '--level', dest='level', default=1,
                        type=int, choices=range(1, 5),
                        help='Select administrative level')
    parser.add_argument('-n', '--name', dest='name', default=None,
                        help='Select region name')
    parser.add_argument('-t', '--types', nargs='+', dest='types',
                        default=None,
                        help='Select road types (list)')
    parser.add_argument('-o', '--output', default='output.csv',
                        help='Output file name')
    parser.add_argument('-d', '--distance', dest='distance', type=int,
                        default=500,
                        help='Distance in meters to split')
    parser.add_argument('--no-header', dest='noheader', action='store_true',
                        help='Output without header at the first row')
    parser.set_defaults(noheader=False)
    parser.add_argument('--plot', dest='plot', action='store_true',
                        help='Plot the output')
    parser.set_defaults(plot=False)

    args = parser.parse_args(argv)

    print(args)

    countries = gadm_get_country_list()

    if args.country not in countries.keys():
        print("All country list :-")
        for c in sorted(countries.keys()):
            print('- {0}'.format(c.encode('utf-8')))
        print("Please specify a country name from above list with -c option.")
        sys.exit(-1)

    if not os.path.exists('data'):
        os.makedirs('data')

    args.ccode = countries[args.country].split('_')[0]
    gadm_shp_file = 'data/{0}_adm_shp.zip'.format(args.ccode)
    if os.path.exists(gadm_shp_file):
        print("Using exists administrative boundary data file...")
    else:
        print("Download administrative boundary data file...")
        gadm_shp_file = gadm_download_country_data(args.ccode)

    zip_file = zipfile.ZipFile(gadm_shp_file, 'r')
    for file in zip_file.namelist():
        for l in range(1, args.level + 1):
            if re.match('.*adm{0}\.(:?dbf|shp)'.format(l), file):
                zip_file.extract(file, 'data')
    zip_file.close()

    osm_shape_filename = ('data/{0}_{1}_osm.shp.zip'
                          .format(args.ccode, args.name))

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

    print("Read and process Roads shapefile...")
    shp = open('data/{0}_{1}_roads.shp'.format(args.ccode, args.name), 'rb')
    dbf = open('data/{0}_{1}_roads.dbf'.format(args.ccode, args.name), 'rb')

    reader = shapefile.Reader(shp=shp, dbf=dbf)

    sr = reader.shapeRecords()

    type_index = 3
    types = set()
    for s in sr:
        name = s.record[type_index]
        types.add(name)
    print("All road types :-")
    for t in types:
        if args.types is None:
            selected = True
        else:
            selected = t in args.types
        print('{0} {1}'.format('*' if selected else '-', t))
    print("You can specify the road types with -t option. (* is selected)")

    lng, lat = sr[0].shape.points[0]
    a, b, zone_x, zone_y = utm.from_latlon(lat, lng)
    utm_zone = "%d%s" % (zone_x, zone_y)

    wgs2utm = partial(pyproj.transform, pyproj.Proj("+init=EPSG:4326"),
                      pyproj.Proj("+proj=utm +zone=%s" % utm_zone))
    utm2wgs = partial(pyproj.transform, pyproj.Proj("+proj=utm +zone=%s" %
                      utm_zone), pyproj.Proj("+init=EPSG:4326"))

    uid = 0
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

    f = open(args.output, 'wb')
    cols = ['segment_id', 'osm_id', 'osm_name', 'osm_type', 'start_lat',
            'start_long', 'end_lat', 'end_long']
    writer = csv.DictWriter(f, fieldnames=cols)
    if not args.noheader:
        writer.writeheader()

    for s in sr:
        r = s.record
        t = r[type_index]
        if road_types is None or t in road_types:
            p = s.shape.points
            line = LineString(p)
            new_line = transform(wgs2utm, line)
            segments = redistribute_vertices(new_line, args.distance)
            osm_id = r[0]
            osm_name = r[1].strip()
            osm_ref = r[2].strip()
            osm_type = r[3].strip()
            #check_length(segments)
            new_segments = transform(utm2wgs, segments)
            uid = output_to_file(writer, uid, osm_id, osm_name, osm_type,
                                 new_segments)
            if args.plot:
                #p = line.coords
                p = new_segments.coords
                x = [i[0] for i in p[:]]
                y = [i[1] for i in p[:]]
                if t not in road_colors:
                    road_colors.append(t)
                c = cvalues[road_colors.index(t) % len(cvalues)]
                if t not in first:
                    first.append(t)
                    ax.plot(x, y, color=c, label=t)
                else:
                    ax.plot(x, y, color=c)
    f.close()

    if args.plot:
        plt.legend(loc='best', fancybox=True, framealpha=0.5)
        plt.title('{0}, {1}'.format(args.name, args.country))
        ax.get_yaxis().get_major_formatter().set_useOffset(False)
        ax.get_yaxis().get_major_formatter().set_scientific(False)
        ax.get_xaxis().get_major_formatter().set_useOffset(False)
        ax.get_xaxis().get_major_formatter().set_scientific(False)
        plt.show()

    print("Done")
    return 0


if __name__ == "__main__":
    sys.exit(main())
