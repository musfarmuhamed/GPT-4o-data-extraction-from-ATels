# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 20:20:38 2024

@author: musfar
"""

"""
This script processes astronomical object data by querying the Simbad database. 
It reads object names from processed ATEL data, retrieves additional information from 
Simbad using the TAP protocol, and saves the queried results to CSV files.

Input:
- Processed ATEL sources in CSV format.
- JSON files containing celestial object data.

Output:
- Two CSV files containing the queried results from Simbad for the specified objects.
"""

import os
import json
import pandas as pd
import glob
from astroquery.simbad import Simbad
from astropy.table import Table

# Load regular source names from the ATEL sources CSV file
df_reg = pd.read_csv("../data/ATEL_SOURCES.csv")

# Get a list of all JSON files in the output directory
files = glob.glob("../output/gpt_output/*.json")

def query_simbad_objects(list_objects):
    """
    Query the Simbad database for a list of celestial objects.

    Parameters:
    list_objects (list): A list of celestial object names.

    Returns:
    DataFrame: A pandas DataFrame containing the results of the Simbad query.
    """
    # Create a Table from the list of objects for querying
    list_of_objects = Table([list_objects], names=["regex_objects"])
    
    # Define the SQL query to be executed on the Simbad TAP service
    query = """SELECT basic."main_id", ident."id", alltypes."otypes", TAP_UPLOAD.mydata.regex_objects
               FROM TAP_UPLOAD.mydata
               LEFT JOIN ident ON TAP_UPLOAD.mydata.regex_objects = ident."id"
               LEFT JOIN basic ON basic."oid" = ident."oidref"
               LEFT JOIN alltypes ON basic."oid" = alltypes."oidref"
            """
    
    # Execute the query and convert the result to a pandas DataFrame
    result = Simbad.query_tap(query, mydata=list_of_objects)
    df_result = result.to_pandas()
    return df_result


# Initialize lists to hold unique object names
all_names_reg = []
all_names_gpt = []

# Process each JSON file to extract celestial object names
for i, file_ in enumerate(files):
    # Extract the base name of the file to match with ATEL sources
    text_id = os.path.basename(file_)[:-5].replace("-", " ")
    
    # Open and read the JSON file
    with open(file_, "r") as i_file:
        dict_ = json.load(i_file)
    
    # Extract object names from the JSON data
    for obj_ in dict_["Celestial Object"]:
        if obj_["Name"]:
            # Encode to ASCII to handle any non-ASCII characters
            all_names_gpt.append(obj_["Name"].encode('ascii', 'replace').decode('ascii'))
            
    # Retrieve corresponding source names from the ATEL data
    tmp_names = df_reg[df_reg["ATELNO"] == text_id]["Sources"].values
    if len(tmp_names) != 0:
        for n_ in tmp_names:
            # Encode to ASCII to ensure uniformity
            all_names_reg.append(n_.encode('ascii', 'replace').decode('ascii'))


# Print the counts of object names found
print(f"GPT Names Count: {len(all_names_gpt)}")
print(f"Regular Names Count: {len(all_names_reg)}")

# Remove duplicates by converting lists to sets and back to lists
all_names_gpt = list(set(all_names_gpt))
all_names_reg = list(set(all_names_reg))


# Print the counts after deduplication
print(f"Unique GPT Names Count: {len(all_names_gpt)}")
print(f"Unique Regular Names Count: {len(all_names_reg)}")

# Query Simbad for the GPT names in batches
df_gpt_1 = query_simbad_objects(all_names_gpt[0:5000])
df_gpt_2 = query_simbad_objects(all_names_gpt[5000:10000])
df_gpt_3 = query_simbad_objects(all_names_gpt[10000:])

# Query Simbad for the regular names in batches
df_reg_1 = query_simbad_objects(all_names_reg[0:5000])
df_reg_2 = query_simbad_objects(all_names_reg[5000:10000])
df_reg_3 = query_simbad_objects(all_names_reg[10000:])

# Concatenate the results from all queries for regular and GPT names
df_reg = pd.concat([df_reg_1, df_reg_2, df_reg_3])
df_gpt = pd.concat([df_gpt_1, df_gpt_2, df_gpt_3])

# Save the resulting DataFrames to CSV files
df_reg.to_csv("../output/REGEX_SOURCES_SIMBAD_FROM_GPT4o_QUERIED_ATELS.csv", index=False)
df_gpt.to_csv("../output/GPT4o_SOURCES_SIMBAD_FROM_GPT4o_QUERIED_ATELS.csv", index=False)
