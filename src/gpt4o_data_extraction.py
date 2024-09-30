# -*- coding: utf-8 -*-
"""
Created on Wed Sep 18 11:13:20 2024

@author: musfar
"""


"""
This program utilizes the OpenAI API to extract information from a dataset of astronomical texts. 
It begins by loading the OpenAI API key from a .env file and reading a CSV file that contains relevant astronomical data. 
By leveraging GPT-4o’s natural language processing capabilities, 
the program efficiently extracts all pertinent sources mentioned in the Astronomer’s Telegrams (ATELs), 
ensuring that both Right Ascension (RA) and Declination (DEC) coordinates are accurately captured.  
The output is generated in JSON format, providing structured information extracted from the text.
"""


import os
import json
import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables from the .env file to access sensitive information
load_dotenv()

# Retrieve the OpenAI API key from environment variables
openai_api_key = os.getenv("OPENAI_API_KEY")

# Check if the API key was successfully retrieved; raise an error if not
if openai_api_key is None:
    raise ValueError("OpenAI API key not found. Please set it in the .env file.")

# Initialize the OpenAI client with the retrieved API key
client = OpenAI(api_key=openai_api_key)



def ask_gpt(body):
    """
    Sends a prompt to the OpenAI API and retrieves the response.
    
    Args:
        body (str): The text input for the model to process.

    Returns:
        dict: The parsed JSON response from the model, or None if an error occurs.
    """
    
    try:
        # Construct the prompt for the API call
        prompt = f"""
        Extract information from the text and provide the output in JSON format as: {{"Celestial Object": [{{"Name": , "RA":, "Dec":, "redshift":, "Type":, "Time":, "Date": }}], "References": , "Event Type":, "Time":, "Date":, "Telescope": ,"Instrument":, "Observatory":}} for all astronomical object names and put Null when there is no information.
        {body}
        """
        
        # Send the prompt to the OpenAI API
        response = client.chat.completions.create(
            model="gpt-4o",  # Specify the model to be used for the API request
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ]
        )
        return response
    except Exception as e:
        # Handle exceptions that may occur during the API call
        print(f"Error communicating with OpenAI API: {e}")
        return None

def extract_information(atels):
    """
    Processes each row of the input DataFrame and extracts information using the OpenAI model.

    Args:
        atels (DataFrame): The DataFrame containing the text data to process.
    """
    # Iterate through each entry in the DataFrame
    for i, (text_id, body) in enumerate(zip(atels.atelno, atels.body)):
        
        # Replace spaces in text_id with hyphens for valid file naming
        text_id = text_id.replace(" ", "-")
        response = ask_gpt(body)  # Call the OpenAI model with the current body of text
        
        if response:
            # Process the response from the model
            answer = response.choices[0].message.content.replace("```", "").replace("json", "")
            #print(text_id, answer)  # Output the response for verification

            try:
                # Load the answer as JSON
                output_dict = json.loads(answer)
                output_file_path = f"../output/{text_id}.json"  # Define the output file path
                
                # Write the JSON output to a file
                with open(output_file_path, "w") as out_file:
                    json.dump(output_dict, out_file, indent=4)
            except json.JSONDecodeError:
                # Handle any JSON decoding errors
                print(f"Failed to decode JSON for {text_id}. Response: {answer}")
        
        # Print progress every 100 records processed
        if i % 100 == 0:
            print(f"Processed {i} out of {len(atels)} records.")

def main():
    # Load the dataset from a CSV file
    try:
        atels = pd.read_csv("../data/Processed_Atels.csv")  # Specify the path to the CSV file
        extract_information(atels)  # Call the function to process the data
    except FileNotFoundError:
        # Handle the case where the specified CSV file does not exist
        print("The specified CSV file was not found. Please check the file path.")
    except Exception as e:
        # Catch any other errors that may occur
        print(f"An error occurred: {e}")

# Entry point for the script
if __name__ == "__main__":
    main()