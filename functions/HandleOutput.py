import os

from Constant import pathPickleByExpe
from classes.OutputFileSQ import *
from functions.LoadTransform import convert_date_columns
import pickle
from functions.ProjectIterator import *
import pandas as pd
from collections import defaultdict
import Constant
from concurrent.futures import ThreadPoolExecutor, as_completed
from joblib import dump, load
from sklearn.metrics import mean_squared_error, r2_score
import numpy as np
from functions import Compare
import matplotlib.pyplot as plt
import seaborn as sns

def load_pickle(file_path):
    with open(file_path, 'rb') as f:
        data = pickle.load(f)
        print(f'{file_path} loaded')
    return data

def parallel_load(file_paths):
    """
    Loads multiple pickle files in parallel using joblib.load.

    Parameters:
        file_paths (dict): A dictionary with descriptive names as keys and file paths as values.

    Returns:
        dict: A dictionary with the same keys as `file_paths`, where each value is the loaded data.
    """

    def load_file(path):
        """Loads a single file using joblib.load and returns its data."""
        try:
            data = load(path)
            print(f'{path} loaded')
            return data
        except Exception as e:
            print(f"Failed to load {path}: {e}")
            return None

    # Dictionary to hold the loaded data
    loaded_data = {}

    # Parallel loading with ThreadPoolExecutor
    with ThreadPoolExecutor() as executor:
        future_to_name = {executor.submit(load_file, path): name for name, path in file_paths.items()}

        for future in as_completed(future_to_name):
            name = future_to_name[future]
            try:
                result = future.result()
                if result is not None:
                    loaded_data[name] = result
                else:
                    print(f"Warning: No data returned for {name}")
            except Exception as e:
                print(f"Error loading {name}: {e}")

    return loaded_data

def merge_with_suffixes(sim, obs, merge_columns=['TRT_NAME', 'CUL_ID'], suffixes=('_sim', '_obs')):
    """
    Merges two DataFrames with the specified suffixes always applied to the columns except for the merge columns.

    Args:
    - sim (pd.DataFrame): The simulation DataFrame.
    - obs (pd.DataFrame): The observation DataFrame.
    - merge_columns (list): List of columns to merge on (default: ['TRT_NAME', 'CUL_ID']).
    - suffixes (tuple): Suffixes to add to overlapping columns (default: ('_sim', '_obs')).

    Returns:
    - pd.DataFrame: Merged DataFrame with suffixes applied to all columns except the merge columns.
    """
    # Perform the merge first
    merged_df = pd.merge(sim, obs, on=merge_columns, suffixes=suffixes)

    # Get the columns to check
    merge_columns_set = set(merge_columns)

    # Go through the columns in the merged dataframe and add suffixes where necessary
    for col in merged_df.columns:
        # Skip the merge columns
        if col not in merge_columns_set:
            if col.endswith(suffixes[0]):  # Column from sim
                continue
            elif col.endswith(suffixes[1]):  # Column from obs
                continue
            else:
                # Add suffixes if no suffix is present (i.e., it is an original column from either DataFrame)
                if col in sim.columns:
                    merged_df.rename(columns={col: f'{col}{suffixes[0]}'}, inplace=True)
                elif col in obs.columns:
                    merged_df.rename(columns={col: f'{col}{suffixes[1]}'}, inplace=True)
    return merged_df

def get_planting_date_column(df, base_col_name='PDATE'):
    """
    Check for the planting date column, considering suffixes like _sim or _obs.

    Args:
    - df (pd.DataFrame): The DataFrame to search for the column.
    - base_col_name (str): The base name of the planting date column.

    Returns:
    - str: The name of the planting date column (with suffix if present).
    """
    for suffix in ['_sim', '_obs']:
        col_name = f'{base_col_name}{suffix}'
        if col_name in df.columns:
            return col_name
    return base_col_name  # If no suffix is found, return the base name


def convert_dates_to_days(df, column_type_dict, planting_date_col='PDATE'):
    """
    Converts date columns to the number of days from planting date (PDATE) and creates DAP columns with suffixes.

    Args:
    - df (pd.DataFrame): The DataFrame containing date columns to convert.
    - column_type_dict (dict): A dictionary with column names as keys and their types as values.
    - planting_date_col (str): The column name that contains the planting date (default: 'PDATE').

    Returns:
    - pd.DataFrame: The DataFrame with new DAP columns added, corresponding to each date column.
    """
    # Check for planting date column in the DataFrame
    planting_date_col = get_planting_date_column(df, base_col_name=planting_date_col)
    if planting_date_col not in df.columns:
        raise KeyError(f"Planting date column '{planting_date_col}' not found in DataFrame.")

    # Convert the planting date column to datetime
    df[planting_date_col] = pd.to_datetime(df[planting_date_col], errors='coerce')

    # Iterate over all columns in the DataFrame
    for date_col in df.columns:
        if date_col.endswith('_sim') or date_col.endswith('_obs'):  # Check for '_sim' or '_obs' suffix
            base_col_name = date_col.rsplit('_', 1)[0]  # Get the base column name (e.g., 'SilkD')

            if base_col_name in column_type_dict and column_type_dict[base_col_name] == 'yyyy-mm-dd':
                # Convert the date column to datetime (if not already)
                df[date_col] = pd.to_datetime(df[date_col], errors='coerce')

                # Calculate the difference in days from PDATE and add the suffix to the new column
                suffix = f'_{date_col.split("_")[-1]}'  # Extract suffix ('_sim' or '_obs')
                day_diff_col = f'{base_col_name}{suffix}_DAP'  # Create the new DAP column name

                # Calculate the day difference and add the new column
                df[day_diff_col] = (df[date_col] - df[planting_date_col]).dt.days

    return df

def save_dict_of_dfs_to_excel(dict_of_dfs, file_path):
    """
    :param dict_of_dfs: Dictionary where the key is the sheet name and the value is a pandas DataFrame to be written to that sheet.
    :param file_path: Path to the Excel file where the dataframes will be saved.
    :return: None
    """
    with pd.ExcelWriter(file_path) as writer:
        for sheet_name, df in dict_of_dfs.items():
            df.to_excel(writer, sheet_name=sheet_name)
    print(f"Data successfully saved to {file_path}")


def convert_to_date(date_series):
    """
    Convert a date column to a pandas datetime format, keeping only the date part (discarding time).
    Handles the situation where the time is included in the date (e.g., '2024-11-07 10:15:00').
    """
    return pd.to_datetime(date_series, errors='coerce').dt.date


def replace_na_with_nan(df):
    """
    Replace 'na', 'NA', 'none', and other variants with NaN values.
    """
    return df.replace({'na': np.nan, 'NA': np.nan, 'none': np.nan, None: np.nan})


def convert_columns(df, col_type_dict):
    """
    Converts columns in the DataFrame based on the provided type dictionary.

    Parameters:
    - df (pd.DataFrame): The DataFrame to be converted.
    - col_type_dict (dict): Dictionary mapping column names to their types/formats.

    Returns:
    - pd.DataFrame: The DataFrame with converted columns.
    """
    # Replace 'na', 'NA', 'none', None with NaN in all columns
    df = replace_na_with_nan(df)

    for col, col_type in col_type_dict.items():
        if col in df.columns:
            if col_type == 'yyyy-mm-dd':
                # If it's a date column, ensure the format is correct
                df[col] = convert_to_date(df[col])  # Convert to date only (no time)
            elif col_type == 'text':
                # Convert to string if it's a text column
                df[col] = df[col].astype(str)
            elif col_type in ['day', '°C', 'kPa', 'MJ/m2', 'unitless']:
                # Convert to numeric where applicable
                df[col] = pd.to_numeric(df[col], errors='coerce')
            # You can add more conditions here for other types as necessary
    return df


def calculate_statistics(merged_df, icasa_unit_summary_dic, name):
    # Create an empty list to store results for each variable
    results = []

    # Total rows in the DataFrame
    N_total = len(merged_df)
    print(N_total)
    # Iterate over each variable in the dictionary
    for var, var_type in icasa_unit_summary_dic.items():
        # Skip 'text' types
        #print(var)
        if var_type == 'text':
            continue

        # Define _sim and _obs columns
        sim_col = f"{var}_sim"
        obs_col = f"{var}_obs"

        # For date variables, use _sim_DAP and _obs_DAP
        if var_type == 'yyyy-mm-dd':
            sim_col += "_DAP"
            obs_col += "_DAP"

        # Ensure both _sim and _obs columns exist in the DataFrame
        if sim_col in merged_df.columns and obs_col in merged_df.columns:

            # Convert columns to numeric, coercing errors to NaN, then drop NaN pairs
            merged_df[sim_col] = pd.to_numeric(merged_df[sim_col], errors='coerce')
            merged_df[obs_col] = pd.to_numeric(merged_df[obs_col], errors='coerce')
            valid_pairs = merged_df[[sim_col, obs_col]].dropna()

            N_valid = len(valid_pairs)
            N_sim = merged_df[sim_col].notna().sum()
            N_obs = merged_df[obs_col].notna().sum()
            print('here', sim_col,N_valid,N_sim,N_obs)
            # Calculate RMSE, R², RRMSE, and PE if there are valid pairs
            if N_valid > 0 and N_obs > 0:
                # Root Mean Square Error (RMSE)
                rmse = np.sqrt(mean_squared_error(valid_pairs[obs_col], valid_pairs[sim_col]))
                obs_mean = valid_pairs[obs_col].mean()
                sim_mean = valid_pairs[sim_col].mean()



                # Relative Root Mean Square Error (RRMSE)
                relative_squared_errors = ((valid_pairs[sim_col] - valid_pairs[obs_col]) / valid_pairs[obs_col]) ** 2
                rrmse = np.sqrt(relative_squared_errors.mean()) * 100
                # Calculate the correlation coefficient matrix
                correlation_matrix = np.corrcoef(valid_pairs[sim_col],  valid_pairs[obs_col])

                r = correlation_matrix[0, 1]
                r_squared = r * r

                ss_res = np.sum((valid_pairs[obs_col] - valid_pairs[sim_col]) ** 2)
                ss_tot_sim = np.sum((valid_pairs[obs_col] - sim_mean) ** 2)
                pe = 1 - (ss_res / ss_tot_sim) if ss_tot_sim != 0 else np.nan
                # Optional: Plot comparison
                color_var = 'TRT_NAME'
                Compare.compare_sim_vs_obs(merged_df, sim_col, obs_col, name, color_var, r_squared, rrmse, pe, N_total, N_sim, N_obs)

                # Append calculated statistics to results
                results.append({
                    'var': var,
                    'RMSE': rmse,
                    'R²': r_squared,
                    'RRMSE(%)': rrmse,
                    'PE': pe,
                    'N_valid': N_valid,
                    'N_sim': N_sim,
                    'N_obs': N_obs,
                    'N_total': N_total
                })

    # Convert the results list to a DataFrame
    results_df = pd.DataFrame(results,
                              columns=['var', 'RMSE', 'R²', 'RRMSE(%)', 'PE', 'N_valid', 'N_sim', 'N_obs', 'N_total'])
    return results_df


def global_summ_plotter_indic(observation, icasa_unit_summary_dic, pathPickleByExpe):
    for key, item in observation.items():
        print(key)
        for file in os.listdir(pathPickleByExpe):
            if file.startswith(key):
                simulation = load(os.path.join(pathPickleByExpe, file))

                ##
                sim = convert_columns(simulation.summ_data, icasa_unit_summary_dic)
                print('sim converted')

                # Convert obs columns in the same way
                obs = convert_columns(item['OBS_SUMMARY'], icasa_unit_summary_dic)
                print('obs converted')

                merged_summ = merge_with_suffixes(sim, obs)
                print('merged')

                name = simulation.name
                merged_summ = convert_dates_to_days(merged_summ, icasa_unit_summary_dic)
                print('date to days')
                print(simulation.name, simulation.input_dir_path)

                output = calculate_statistics(merged_summ, icasa_unit_summary_dic, name)
                print(output[['var', 'R²', 'RRMSE(%)', 'PE', 'N_valid', 'N_sim', 'N_obs',
       'N_total']])

                plt.figure(figsize=(4, 10))
                unique_ids = merged_summ["TRT_NAME"].unique()
                colors = plt.cm.get_cmap('tab20', len(unique_ids))  # Using 'tab20' for better color separation
                color_mapping = {cul_id: colors(i) for i, cul_id in enumerate(unique_ids)}
                handles = [plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color_mapping[c], markersize=10)
                           for c in unique_ids]
                plt.legend(handles, unique_ids, title="TRT_NAME")
                plt.show()

def daily_evo_profile(observation, icasa_unit_summary_dic, pathPickleByExpe):
    for key, item in observation.items():
        for file in os.listdir(pathPickleByExpe):

            if file.startswith(key) and key == 'PG':
                simulation = load(os.path.join(pathPickleByExpe, file))
                obs = convert_columns(item['OBS_DAILY'], icasa_unit_summary_dic)
                groupped_obs = obs.groupby(['TRT_NAME', 'CUL_ID'])

                for (trt, cul), group in groupped_obs:
                    print(trt, cul)
                    if trt in simulation.dailys and cul in simulation.dailys[trt]:
                        sim = convert_columns(simulation.dailys[trt][cul].leaves, icasa_unit_summary_dic)
                        sim_tt = convert_columns(simulation.dailys[trt][cul].data, icasa_unit_summary_dic)

                        curr_summ = simulation.summ_data[(simulation.summ_data['TRT_NAME'] == trt) &
                                                         (simulation.summ_data['CUL_ID'] == cul)].head(1)
                        curr_obs = item['OBS_SUMMARY'][(item['OBS_SUMMARY']['TRT_NAME'] == trt) &
                                                       (item['OBS_SUMMARY']['CUL_ID'] == cul)].head(1)
                        print(curr_obs['ADAT'])

                        plot_leaf_profile(sim, curr_summ, curr_obs,trt,cul,None)
                    else:
                        print(f"Pair (TRT_NAME: {trt}, CUL_ID: {cul}) not found in simulation.dailys.")


def plot_leaf_profile(df, sim_summ, obs_summ,trt,cul, tt_df):
    segments = split_dataframe_by_date(df)
    length_df = segments[1]

    # Ensure correct datetime format and numeric columns
    length_df.loc[:, 'yyyy-mm-dd'] = pd.to_datetime(length_df['yyyy-mm-dd'], errors='coerce')
    length_df.iloc[:, 1:] = length_df.iloc[:, 1:].apply(pd.to_numeric, errors='coerce')

    # Create the primary plot (Layer Length vs Date)
    fig, ax1 = plt.subplots(figsize=(10, 6))

    # Plot layer lengths on the primary y-axis (left side)
    for layer in length_df.columns[1:]:
        ax1.plot(length_df['yyyy-mm-dd'], length_df[layer], label=layer)

    ax1.set_xlabel('Date')
    ax1.set_ylabel('Layer Length', color='black')
    ax1.set_title(f'Leaf Length; {trt} {cul}')
    ax1.legend(title='Layers', loc='upper left')
    ax1.grid(True)

    # Set y-limits and ticks based on the layer length data
    min_y, max_y = length_df.iloc[:, 1:].min().min(), length_df.iloc[:, 1:].max().max()
    if np.isfinite(min_y) and np.isfinite(max_y):
        ax1.set_ylim(min_y, max_y)
        ax1.set_yticks(np.linspace(min_y, max_y, num=10))  # Adjust y-ticks for the layer length

    # Plot important dates for sim_summ and obs_summ
    plot_important_dates(sim_summ, 'red', ax1)
    plot_important_dates(obs_summ, 'blue', ax1)

    # If TT data is provided, plot it on the secondary y-axis
    if tt_df is not None:
        ax2 = ax1.twinx()  # Create secondary y-axis for TT data
        tt_df['DATE'] = pd.to_datetime(tt_df['DATE'], errors='coerce')
        ax2.plot(tt_df['DATE'], tt_df['CDVD'], color='green', label='Thermal Time (TT)', linestyle='-', linewidth=2)

        # Ensure that 'CDVD' column is numeric
        tt_df['CDVD'] = pd.to_numeric(tt_df['CDVD'], errors='coerce')

        max_tt = tt_df['CDVD'].max()
        print(f'Max Thermal Time (TT): {max_tt}')  # Debugging output for max TT

        # Set the secondary y-axis label
        ax2.set_ylabel('Air Thermal Time (CDVD)', color='green')
        min_tt, max_tt = tt_df['CDVD'].min(), tt_df['CDVD'].max()
        if np.isfinite(min_tt) and np.isfinite(max_tt):

            ax2.set_yticks(np.linspace(min_tt, max_tt, num=1))  # Adjust y-ticks for Thermal Time (TT)

        # Add a legend for the secondary y-axis (TT)
        ax2.legend(loc='upper right')

    # Final plot adjustments
    plt.tight_layout()
    plt.show()


def split_dataframe_by_date(df):
    segments = []
    start_idx = 0
    for i, col in enumerate(df.columns):
        if col == 'yyyy-mm-dd':
            if start_idx != i:
                segments.append(df.iloc[:, start_idx:i])
            start_idx = i
    if start_idx < len(df.columns):
        segments.append(df.iloc[:, start_idx:])
    return segments


def plot_important_dates(df, color, ax1):
    important_cols = ['ADAT', 'PDATE', 'SilkD', 'MDAT']

    # Initialize y_offset to control the vertical placement of annotations
    y_offset = -5  # Set negative to place below the x-axis
    y_increment = -10  # Adjust this for spacing between annotations

    # Loop through the columns in the dataframe
    for col in df.columns:
        # Check if the column is in the important_cols list
        if col in important_cols:
            # Convert the column values to datetime
            dates_value = pd.to_datetime(df[col], errors='coerce')

            # Drop NaT (Not a Time) values
            dates_value = dates_value.dropna()

            # Plot each date with an annotation
            for date in dates_value:
                ax1.axvline(x=date, color=color, linestyle='--', linewidth=1)

                # Annotate the date with the actual column name below the x-axis
                ax1.annotate(f'{col}', xy=(date, ax1.get_ylim()[0]),
                             xytext=(date, ax1.get_ylim()[0] + y_offset),
                             arrowprops=dict(arrowstyle='->', color=color),
                             color=color, fontsize=10, ha='center')

                # Increment the y_offset to avoid overlap (move further down)
                y_offset += y_increment


def daily_obs_adjusted(observation,  pathPickleByExpe):
    merged_dfs = {}  # Dictionary to store merged DataFrames by experiment

    for key, item in observation.items():
        # Load the corresponding simulation file for the experiment
        for file in os.listdir(pathPickleByExpe):
            if file.startswith(key):
                simulation = load(os.path.join(pathPickleByExpe, file))

                # Prepare a list to store merged DataFrames for each group
                merged_groups = []

                # Group the observation data by TRT_NAME and CUL_ID
                grouped_obs = item['OBS_DAILY'].groupby(['TRT_NAME', 'CUL_ID'])

                for (trt, cul), obs_group in grouped_obs:
                    # Check if the simulation data has the required TRT_NAME and CUL_ID
                    if trt in simulation.dailys and cul in simulation.dailys[trt]:
                        # Extract simulation daily data for the treatment and cultivar
                        daily_sim = simulation.dailys[trt][cul].data

                        # Ensure 'DATE' columns are in datetime format for both data sets
                        obs_group['DATE'] = pd.to_datetime(obs_group['DATE'], errors='coerce')

                        # Rename 'LInoSD' to 'LNUM' in obs_group if it exists
                        obs_group.rename(columns={'TnoSD': 'LNUM'}, inplace=True)
                        #obs_group.rename(columns={'LnoSD': 'LNUM'}, inplace=True)
                        daily_sim['DATE'] = pd.to_datetime(daily_sim['DATE'], errors='coerce')

                        # Merge on 'DATE', 'TRT_NAME', and 'CUL_ID' columns with suffixes
                        merged_group = merge_with_suffixes(daily_sim, obs_group,
                                                           merge_columns=['DATE', 'TRT_NAME', 'CUL_ID'],
                                                           suffixes=('_sim', '_obs'))

                        # Optionally adjust units using icasa_unit_summary_dic if needed

                        # Append the merged group DataFrame to the list
                        merged_groups.append(merged_group)

                # Concatenate all merged groups for the current experiment
                merged_dfs[key] = pd.concat(merged_groups, ignore_index=True)
                print(f"Merged data for experiment {key} completed.")

    return merged_dfs

    ## NEW Simulation formalism

