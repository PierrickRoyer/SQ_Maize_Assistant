import os
import pandas as pd
from datetime import datetime
import math


def calculate_rh(tmin, meanT):
    """Calculate relative humidity (rh) from tmin and meanT."""
    numerator = math.exp((17.625 * tmin) / (243.04 + tmin))
    denominator = math.exp((17.625 * meanT) / (243.04 + meanT))
    rh = 100 * (numerator / denominator)
    return rh


def calculate_vprsd(vp, tmin, tmax):
    """Calculate VPRSD from vapor pressure (vp), tmin, and tmax."""
    # Calculate mean temperature as the average of tmin and tmax
    meanT = (tmin + tmax) / 2
    rh = calculate_rh(tmin, meanT)
    VPRSD = (vp * 100) / (10 * rh)
    return VPRSD


def process_file(file_path):
    """Process the input file, calculate VPRSD, and return the DataFrame."""
    # Read the data from the text file
    df = pd.read_csv(file_path, delim_whitespace=True, header=None,
                     names=['Year', 'Day_Number', 'TMIN', 'TMAX', 'RAIN', 'SRAD', 'WIND', 'VP'])

    # Convert Year and Day_Number to integers
    df['Year'] = df['Year'].astype(str)
    df['Day_Number'] = df['Day_Number'].astype(str)
    print(df)
    # Extract the filename to use for WST_DATASET
    filename = file_path.split('/')[-1].replace('.txt', '')

    # Convert Year and Day_Number to W_DATE (date format)
    df['W_DATE'] = df.apply(
        lambda row: datetime.strptime(f"{row['Year']}-{row['Day_Number']}", '%Y-%j').strftime('%d/%m/%Y'), axis=1)

    # Calculate VPRSD for each row
    df['VPRSD'] = df.apply(lambda row: calculate_vprsd(row['VP'], row['TMIN'], row['TMAX']), axis=1)

    # Add WST_DATASET column
    df['WST_DATASET'] = filename

    # Reorder columns to match the desired format
    df = df[['WST_DATASET', 'W_DATE', 'SRAD', 'TMAX', 'TMIN', 'RAIN', 'VPRSD', 'WIND']]

    return df


def process_directory(directory_path):
    """Loop through the directory, process files with a 20-character name length, and save the combined DataFrame."""
    combined_df = pd.DataFrame()  # Initialize an empty DataFrame

    # Loop through all files in the directory
    for filename in os.listdir(directory_path):
        file_path = os.path.join(directory_path, filename)

        # Check if the file name length is 20 characters and if it is a file
        if len(filename) == 20 and os.path.isfile(file_path):
            print(f"Processing file: {filename}")

            # Process each file and append to the combined DataFrame
            df = process_file(file_path)
            combined_df = pd.concat([combined_df, df], ignore_index=True)

    # Save the combined DataFrame to a CSV file
    output_file = os.path.join("C:/Users/royerpie/Documents/rootDoc/automate/myOutput/", "combined_output.csv")
    combined_df.to_csv(output_file, index=False)
    print(f"Combined file saved as {output_file}")


# Example usage:
directory_path = 'U:\Membres_actuels\Pierrick_Royer\Stage_2022\Passation_P_Royer\Sirius\Project/2-WeatherData/'  # Replace with the correct directory path
process_directory(directory_path)