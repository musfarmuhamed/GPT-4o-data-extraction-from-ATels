# -*- coding: utf-8 -*-
"""
Created on Wed Sep 19 15:58:40 2024

@author: musfar
"""


from astropy.coordinates import SkyCoord

def convert_into_deg(data):
    """
    Convert Right Ascension (RA) and Declination (Dec) from various formats to degrees.

    Parameters:
    data (dict): A dictionary containing astronomical object information.
                  Expected format: {'name': 'BL Lac', 'RA': '22h02m43.291s', 'Dec': '+42d16m39.63s'}

    Returns:
    dict: The input dictionary with RA and Dec converted to degrees.
    """

    # Extract RA and Dec from the input data
    ra_coord = data['RA']
    dec_coord = data['Dec']
    
    # Check if RA is in hour-minute-second format (contains 'h')
    if 'h' in ra_coord:
        # Create a SkyCoord object assuming RA and Dec are in ICRS frame
        coord = SkyCoord(ra=ra_coord, dec=dec_coord, frame='icrs')
        # Update RA and Dec in the data dictionary to degrees
        data['RA'] = coord.ra.deg
        data['Dec'] = coord.dec.deg
        return data
    
    # Check if RA is in degree format (contains ':')
    elif ':' in ra_coord:
        # Create a SkyCoord object assuming RA is in hour angle and Dec is in degrees
        coord = SkyCoord(ra=ra_coord, dec=dec_coord, frame='icrs', unit=('hourangle', 'deg'))
        # Update RA and Dec in the data dictionary to degrees
        data['RA'] = coord.ra.deg
        data['Dec'] = coord.dec.deg
        return data
    
    # If RA and Dec are already in float format
    else:
        # Convert RA and Dec to float values and update the data dictionary
        data['RA'] = float(ra_coord)
        data['Dec'] = float(dec_coord)
        return data

    # Example return format:
    # {'name': 'BL Lac', 'RA': 330.6803791666666, 'Dec': 42.277771666666666}

