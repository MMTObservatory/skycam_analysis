#!/usr/bin/env python

import warnings
import argparse
from pathlib import Path
from datetime import datetime

import numpy as np
import scipy

from astropy.io import fits
from astropy.stats import sigma_clipped_stats
from astropy.utils import iers
from photutils import IRAFStarFinder


warnings.filterwarnings('ignore')
iers.conf.auto_download = False
iers.conf.auto_max_age = None


# need different WCS solutions for different eras. 2011-2012 are the same. unsure of 2014. 2015 and 2016 are different.
# it looks like 2017-2020 is pretty stable, but slight shifts are noticable. looks like 2019 and 2020 are close enough to
# share a solution.

REGIONS = {
    # This is a region low in the north above the brightest part of Tucson's sky glow
    'Tucson': {
        'x': slice(320, 335),
        'y': slice(423, 433)
    },

    # Large region centered on Polaris
    'Polaris': {
        'x': slice(293-15, 293+15),
        'y': slice(406-15, 406+15)
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
    hdr = ""
    for c in CARDS:
        hdr += f"{c},"

    for r in REGIONS:
        for s in ["mean", "median", "stddev"]:
            hdr += f"{r}_{s},"
    hdr += "Polaris_mag,Polaris_flux,Polaris_peak,Polaris_x,Polaris_y,"
    hdr += "filename"
    return hdr


def process_file(filename):
    """
    Process FITS file to get desired header info and image statistics
    """
    outstr = ""
    with fits.open(filename) as hdul:
        hdr = hdul[0].header
        if hdr['NAXIS'] == 3:
            im = np.flipud(hdul[0].data[:, :, 0])
        else:
            im = hdul[0].data

        for c in CARDS:
            outstr += f"{hdr[c]},"

        for k, r in REGIONS.items():
            cutout = im[r['y'], r['x']]
            im_mean, im_med, im_std = sigma_clipped_stats(cutout, sigma=3, maxiters=5)
            outstr += f"{im_mean:.3f},{im_med:.3f},{im_std:.3f},"

        subim = im[REGIONS['Polaris']['y'], REGIONS['Polaris']['x']]
        mean, median, std = sigma_clipped_stats(subim, sigma=3, maxiters=10)
        finder = IRAFStarFinder(fwhm=2.0, threshold=5*std)
        try:
            sources = finder(subim - median)
            if sources is not None:
                sources.sort(['mag'])
                polaris = sources[0]
                for k in ['mag', 'flux', 'peak', 'xcentroid', 'ycentroid']:
                    outstr += f"{polaris[k]:.3f},"
            else:
                outstr += ",,,,,"
        except:
            outstr += ",,,,,"
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
