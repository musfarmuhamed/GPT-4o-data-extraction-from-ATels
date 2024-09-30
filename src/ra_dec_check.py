# -*- coding: utf-8 -*-
"""
Created on Thrusday Sep 19 14:07:46 2024

@author: musfar
"""    
    
"""
This script processes JSON data of celestial objects associated with ATEL alerts.
It checks the Right Ascension (RA) and Declination (Dec) values against the alert body
and categorizes the data into good, bad, or null entries.

Input:
- Processed ATEL sources in CSV format.
- JSON files containing celestial object data.

Output:
- Three JSON files categorizing the entries: good, bad, and null.
"""

import os
import pandas as pd
import json
import numpy as np 


def check_text_for_ra_dec(atelnum, atel_name, json_data):
    """
    Check the JSON data for valid RA and Dec values against the ATEL alert body.

    Parameters:
    atelnum (int): The ATEL number.
    atel_name (str): The name of the ATEL alert.
    json_data (list): A list of celestial object data in JSON format.

    Returns:
    tuple: Three dictionaries containing good, bad, and null entries, along with a count array.
    """
    # Retrieve the body of the ATEL alert
    atel_body = df.loc[df['atelno'] == atel_name, 'body'].values[0]
    
    # Initialize counts for categorization: [all, good, bad, null]
    count = np.array([0, 0, 0, 0])
    
    # Initialize dictionaries for categorizing entries
    json_data_bad = {"ATEL%05i" % atelnum: []}
    json_data_good = {"ATEL%05i" % atelnum: []}
    json_data_null = {"ATEL%05i" % atelnum: []}
    
    # Process each entry in the JSON data
    for entry in json_data:
        count[0] += 1  # Count all entries
        ra = entry.get('RA')
        dec = entry.get('Dec')

        # Check for null RA and Dec values
        if ra is None or dec is None:
            json_data_null["ATEL%05i" % atelnum].append(entry)
            count[3] += 1
            continue
        
        # Check if RA and Dec are lists or dictionaries (bad cases)
        if isinstance(ra, (list, dict)):
            json_data_good["ATEL%05i" % atelnum].append(entry)
            count[2] += 1
            continue
        
        # Check if RA and Dec are valid floats or integers
        if isinstance(ra, (float, int)) and isinstance(dec, (float, int)):
            if str(ra) in atel_body and str(dec) in atel_body:
                json_data_good["ATEL%05i" % atelnum].append(entry)
                count[1] += 1
            else:
                json_data_bad["ATEL%05i" % atelnum].append(entry)
                count[2] += 1
            continue
        
        # Additional checks for RA starting with 'J' or matching criteria
        if ra[0] == "J":
            json_data_bad["ATEL%05i" % atelnum].append(entry)
            count[2] += 1
        elif ra[:5] == dec[:5] :
            json_data_bad["ATEL%05i" % atelnum].append(entry)
            count[2] += 1
        elif ra[:3] in atel_body and dec[:3] in atel_body:
            json_data_good["ATEL%05i" % atelnum].append(entry)
            count[1] += 1
        else:
            json_data_bad["ATEL%05i" % atelnum].append(entry)
            count[2] += 1

    return json_data_good, json_data_bad, json_data_null, count

            

def main():
    # Load processed ATEL data
    global df
    df = pd.read_csv("../data/Processed_Atels.csv") 

    path_to_json = '../output/gpt_output/'
    json_files = [f for f in os.listdir(path_to_json) if f.endswith('.json')]
    
    print(f"Number of JSON files: {len(json_files)}")

    # Initialize lists to hold categorized data
    json_good_all = []
    json_bad_all = []
    json_null_all = []

    # Overall counts: [all, good, bad, null]
    count_all = np.array([0, 0, 0, 0])
    
    for json_file in json_files:
        with open(os.path.join(path_to_json, json_file)) as f:
            data = json.load(f)
            atel_name = json_file.strip(".json").replace("-", " ")
            atel_no = int(atel_name.strip("ATEL #"))

            # Extract celestial objects and update with additional data
            data_all_sources = data.pop("Celestial Object")
            for obj in data_all_sources:
                obj.update(data)

            # Check and categorize RA and Dec values
            j_good, j_bad, j_null, counts = check_text_for_ra_dec(atel_no, atel_name, data_all_sources)
            if j_good["ATEL%05i" % atel_no]:
                json_good_all.append(j_good)
            if j_bad["ATEL%05i" % atel_no]:
                json_bad_all.append(j_bad)
            if j_null["ATEL%05i" % atel_no]:
                json_null_all.append(j_null)

            count_all += counts

    # Print summary of counts
    print("Total count: all, good, bad, null")
    print(count_all)
    print(f"Number of ATEL Alerts: {len(json_files)}")
    
    # # Save categorized results to JSON files
    # with open("output/ATEL_good.json", 'w') as json_file:
    #     json.dump(json_good_all, json_file, indent=4)

    # with open("output/ATEL_bad.json", 'w') as json_file:
    #     json.dump(json_bad_all, json_file, indent=4)

    # with open("output/ATEL_null.json", 'w') as json_file:
    #     json.dump(json_null_all, json_file, indent=4)




# Run the main process
if __name__ == "__main__":
    main()
