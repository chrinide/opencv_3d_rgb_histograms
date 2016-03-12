#! /usr/bin/env python
# vim: set fileencoding=utf-8 :
from __future__ import print_function
from __future__ import unicode_literals
usage = """\
Builds a matrix of 3d rgb histogram distances for all images in the
directory passed in.
"""
import argparse
import os
import logging
import glob
import csv

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
parser.add_argument("image_directory", help="directory of images")
parser.add_argument("outfile", type=argparse.FileType('w'),
                    default="distances.csv", help="CSV output file")

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
    imgarray = cv2.imread(image)
    hist = cv2.calcHist([imgarray], [0, 1, 2], None,
                        [bins, bins, bins],
                        [0, 256, 0, 256, 0, 256])
    hist = cv2.normalize(hist, hist)

    return hist.flatten()


def chi2_distance(a, b, eps=1e-10):
    """ distance between two histograms (a, b) """
    d = 0.5 * np.sum([((x - y) ** 2) / (x + y + eps)
                      for (x, y) in zip(a, b)])

    return d

files = glob.glob("{d}/*.jpg".format(d=args.image_directory))
histograms = {}
for filename in files:
    (d, f) = os.path.split(filename)
    logger.info("calculating histogram for {f}".format(f=filename))
    histograms[f] = get_histogram(filename, args.bins)

csv_out = csv.writer(args.outfile)
csv_out.writerow(("a", "b", "distance"))
for a in histograms:
    logger.info("calculating distances for {f}".format(f=a))
    for b in histograms:
        if a != b:
            d = chi2_distance(histograms[a], histograms[b])
            csv_out.writerow((a, b, d))
