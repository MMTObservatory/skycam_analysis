#!/usr/bin/env python

import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import scipy

from astropy.io import fits
from astropy.stats import sigma_clipped_stats


REGIONS = {
    # This is a region low in the north above the brightest part of Tucson's sky glow
    'Tucson': {
        'x': slice(320, 335),
        'y': slice(423, 433)
    },

    # This region is low in the SSW above the brightest part of Nogales's sky glow
    'Nogales': {
        'x': slice(350, 365),
        'y': slice(40, 50)
    },

    # This is a region centered at the zenith position in the image
    'Zenith': {
        'x': slice(304-10, 304+10),
        'y': slice(238-10, 238+10)
    },

    # This is a region in the SE at an elevation of about 45 deg and about midway between Tucson and Nogales
    'SE': {
        'x': slice(161-10, 161+10),
        'y': slice(177-10, 177+10)
    },

    # This is a region in the WNW at about 45 deg and midway between Tucson and Nogales
    'WNW': {
        'x': slice(485-10, 485+10),
        'y': slice(250-10, 250+10)
    }
}


# The header cards we want to grab
CARDS = [
    'UT',
    'GAIN',
    'FRAME',
    'LST',
    'AZ',
    'EL',
    'SCOPEX',
    'SCOPEY',
]


def mk_header():
    """
    Generate CSV header string
    """
    hdr = "# "
    for c in CARDS:
        hdr += f"{c},"

    for r in REGIONS:
        for s in ["mean", "median", "stddev"]:
            hdr += f"{r}_{s},"
    hdr += "CREATE TIME,"
    hdr += "filename"
    return hdr


def process_file(filename):
    """
    Process FITS file to get desired header info and image statistics
    """
    outstr = ""
    with fits.open(filename) as hdul:
        im = hdul[0].data
        hdr = hdul[0].header

        for c in CARDS:
            outstr += f"{hdr[c]},"

        for k, r in REGIONS.items():
            cutout = im[r['y'], r['x']]
            im_mean, im_med, im_std = sigma_clipped_stats(cutout, sigma=3, maxiters=5)
            outstr += f"{im_mean:.3f},{im_med:.3f},{im_std:.3f},"
        ts = datetime.fromtimestamp(Path(filename).stat().st_ctime)
        outstr += f"{ts.isoformat()},"
        outstr += f"{filename}"

    return outstr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Grab header and image statistics from MMTO skycam image")
    group = parser.add_mutually_exclusive_group()
    group.add_argument('-f', '--filename', help="FITS image from MMTO skycam")
    group.add_argument('-d', '--directory', help="Process all FITS files in a directory")
    parser.add_argument('--header', action="store_true", help="Add header string to output")
    parser.add_argument('-z', '--uncompress', action="store_true", help="Operate on .fits.gz files")
    args = parser.parse_args()

    if args.header:
        print(mk_header())

    if args.filename is not None:
        print(process_file(args.filename))

    if args.directory is not None:
        if args.uncompress:
            files = sorted(Path(args.directory).glob("*.fits.gz"))
        else:
            files = sorted(Path(args.directory).glob("*.fits"))
        for f in files:
            print(process_file(f))
