#!/usr/bin/env python

import argparse

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
    hdr = "# "
    for c in CARDS:
        hdr += f"{c},"

    for r in REGIONS:
        for s in ["mean", "median", "stddev"]:
            hdr += f"{r}_{s},"

    hdr += "filename"
    return hdr


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Grab header and image statistics from MMTO skycam image")
    parser.add_argument('-f', '--filename', help="FITS image from MMTO skycam")
    parser.add_argument('--header', action="store_true", help="Add header string to output")
    args = parser.parse_args()

    if args.header:
        print(mk_header())

    if args.filename is not None:
        outstr = ""
        with fits.open(args.filename) as hdul:
            im = hdul[0].data
            hdr = hdul[0].header

            for c in CARDS:
                outstr += f"{hdr[c]},"

            for k, r in REGIONS.items():
                cutout = im[r['y'], r['x']]
                im_mean, im_med, im_std = sigma_clipped_stats(cutout, sigma=3, maxiters=5)
                outstr += f"{im_mean:.3f},{im_med:.3f},{im_std:.3f},"
            outstr += f"{args.filename}"

        print(outstr)
