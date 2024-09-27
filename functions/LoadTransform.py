import pandas as pd
import Constant
import os


def convert_date_columns(df, format):
    # Find columns that contain the substring 'DAT'
    date_columns = [col for col in df.columns if 'DAT' in col]

    for col in date_columns:
        try:
            # Explicitly convert to datetime using the format 'dd/mm/yyyy'
            df[col] = pd.to_datetime(df[col], format=format, errors='coerce')
        except Exception as e:
            print(f"Error converting column {col}: {e}")

    return df
def load_sim_summ_csv(path, sep, start_str, encod):
    # Open the file and search for the line that starts with the specified string
    with open(path, 'r', encoding=encod) as file:
        for idx, line in enumerate(file):
            if line.startswith(start_str):
                header_line = idx
                break
        else:
            raise ValueError(f"No line starts with '{start_str}' in the file.")
    # Read the CSV using the detected header line
    obs = pd.read_csv(path, sep=sep, encoding = encod, header=header_line)
    print(obs)
    return obs


def load_sim_summ_SQ(path,start_str, encod):
    with open(path, 'r', encoding=encod) as f:
        lines = f.readlines()
    header_line = None
    for i, line in enumerate(lines):
        if start_str in line:
            header_line = i
            break

    # Load the file into a DataFrame starting from the header line
    if header_line is not None:
        df = pd.read_csv(path, sep='\t',encoding = encod, skiprows=header_line, header=0)
        #print(df)
        return df
    else:
        print("t'es baisé, mauvais format, certainemùent le start_str" )
        return None


def load_Jugurta_arborescence(rootPath, start_str,encod):
    all_dfs = []

    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(rootPath):
        for file in filenames:
            if "Summary_output" in file and file.endswith('.sqbrs'):
                file_path = os.path.join(dirpath, file)
                df = load_sim_summ_SQ(file_path,start_str,encod)
                if df is not None:
                    all_dfs.append(df)

    if all_dfs:
        # Concatenate all DataFrames into one
        concatenated_df = pd.concat(all_dfs, ignore_index=True)
        print(concatenated_df)
        return concatenated_df
    else:
        print("No valid files found.")
        return None

def load_Pierrick_arborescence(rootPath, start_str,encod):
    all_dfs = []

    # Walk through the directory tree
    for dirpath, dirnames, filenames in os.walk(rootPath):
        for file in filenames:
            if "file" in file:
                file_path = os.path.join(dirpath, file)
                df = load_sim_summ_SQ(file_path,start_str,encod)
                if df is not None:
                    all_dfs.append(df)

    if all_dfs:
        # Concatenate all DataFrames into one
        concatenated_df = pd.concat(all_dfs, ignore_index=True)
        print(concatenated_df)
        return concatenated_df
    else:
        print("No valid files found.")
        return None






