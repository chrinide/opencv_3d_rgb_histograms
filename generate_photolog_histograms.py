#! /usr/bin/env python
# vim: set fileencoding=utf-8 :
from __future__ import print_function
from __future__ import unicode_literals
usage = """\
Generates histograms for all valid photos in the photolog database
and inserts them into the photolog_histograms table.
"""
import argparse
import os
import logging
import re

import psycopg2
import psycopg2.extras

import numpy as np
import cv2

parser = argparse.ArgumentParser(
    description=usage,
    formatter_class=argparse.RawDescriptionHelpFormatter)
group = parser.add_mutually_exclusive_group()
group.add_argument("-v", "--verbose", action="store_true", dest="verbose",
                   default=True, help="be more verbose")
group.add_argument("-q", "--quiet", action="store_false", dest="verbose",
                   default=True, help="be quiet")
parser.add_argument("-b", "--bins", dest="bins", type=int, default=8,
                    help="number of bins across each dimension in histogram")
parser.add_argument("-u", "--update", dest="dbupdate", action="store_true",
                    default=False, help="update the database, instead of insert")
parser.add_argument("image_directory", help="directory of images")

args = parser.parse_args()

if args.verbose:
    logger = logging.getLogger('root')
    logger.setLevel(logging.INFO)
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter("%(name)-12s: %(levelname)-8s %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)


def get_histogram(image, bins):
    """ calculate a 3d RGB histogram from an image """
    if os.path.exists(image):
        imgarray = cv2.imread(image)

        hist = cv2.calcHist([imgarray], [0, 1, 2], None,
                            [bins, bins, bins],
                            [0, 256, 0, 256, 0, 256])
        hist = cv2.normalize(hist, hist)

        return hist.flatten()
    else:
        return None


def chi2_distance(a, b, eps=1e-10):
    """ distance between two histograms (a, b) """
    d = 0.5 * np.sum([((x - y) ** 2) / (x + y + eps)
                      for (x, y) in zip(a, b)])

    return d

photolog = psycopg2.connect(
    host='example.com', database='photos',
    port=5432, user='username',
    cursor_factory=psycopg2.extras.DictCursor,
    application_name=os.path.basename(__file__))
cursor = photolog.cursor()
insert_cursor = photolog.cursor()
query = ("SELECT id, path "
         "FROM photolog_photos "
         "WHERE include = TRUE")
params = ()
if not args.dbupdate:
    query += (" AND id NOT IN "
              "(SELECT id FROM photolog_histograms "
              " WHERE bins = %s)")
    params = (args.bins,)
cursor.execute(query, params)
for row in cursor:
    (photo_id, path) = row
    basename = re.sub('.*/img/photolog/([0-9]{4})/([0-9]{2})/(.*)',
                      '\\1_\\2_\\3.jpg', path)
    filename = os.path.join(args.image_directory, basename)

    (d, f) = os.path.split(filename)
    logger.info("calculating histogram for {f}".format(f=filename))
    histogram = get_histogram(filename, args.bins)
    if histogram is not None:
        h = [float(x) for x in histogram]

        if args.dbupdate:
            query = ("UPDATE photolog_histograms "
                     "SET rgb_histogram = %s "
                     "WHERE id = %s AND bins = %s")
            params = (h, photo_id, args.bins)
        else:
            query = ("INSERT INTO photolog_histograms "
                     "(id, bins, rgb_histogram) "
                     "VALUES (%s, %s, %s)")
            params = (photo_id, args.bins, h)
        try:
            insert_cursor.execute(query, params)
        except Exception as e:
            print("error: {e}".format(e=e))
            photolog.rollback()
        else:
            photolog.commit()
    else:
        logger.info("warning, couldn't find {f}".format(f=filename))

cursor.close()
insert_cursor.close()
photolog.close()
