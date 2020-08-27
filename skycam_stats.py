#!/usr/bin/env python

import argparse

import numpy as np
import scipy

from astropy.io import fits


# This is a region low in the north above the brightest part of Tucson's sky glow
TUCSON = {
    'x': slice(320, 335),
    'y': slice(423, 433)
}

# This region is low in the SSW above the brightest part of Nogales's sky glow
NOGALES = {
    'x': slice(350, 365),
    'y': slice(40, 50)
}

# This is a region centered at the zenith position in the image
ZENITH = {
    'x': slice(304-10, 304+10),
    'y': slice(238-10, 238+10)
}

# This is a region in the SE at an elevation of about 45 deg and about midway between Tucson and Nogales
SE = {
    'x': slice(161-10, 161+10),
    'y': slice(177-10, 177+10)
}

# This is a region in the WNW at about 45 deg and midway between Tucson and Nogales
WNW = {
    'x': slice(485-10, 485+10),
    'y': slice(250-10, 250+10)