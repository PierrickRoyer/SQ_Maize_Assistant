import pandas as pd
from lxml import etree
from collections import defaultdict
import os


def read_xml_to_df(file_path):
    parser = etree.XMLParser(remove_blank_text=True)  # To preserve formatting
    tree = etree.parse(file_path, parser)
    root = tree.getroot()

    # Extract data into a list for DataFrame creation
    data = []
    for item in root.xpath('//CropParameterItem'):
        param_name = item.get('name')
        for param in item.xpath('ParamValue/Item'):
            key = param.xpath('Key/string')[0].text
            value = param.xpath('Value/double')[0].text
            data.append([param_name, key, float(value)])

    # Create DataFrame
    df = pd.DataFrame(data, columns=['Variety', 'Parameter', 'Value'])

    return df, tree

# Function to rewrite the XML while preserving the namespaces and XML declaration
def rewrite_xml(tree, output_file):
    # Open the file in write mode
    with open(output_file, 'wb') as f:
        # Manually write the XML declaration without encoding
        f.write(b'<?xml version="1.0"?>\n')

        # Write the rest of the XML tree, without specifying encoding
        tree.write(f, pretty_print=True, xml_declaration=False)

def read_genotype_parameters(file_path):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()

    # Dictionary to store parameters for each genotype
    genotype_params = defaultdict(dict)

    # Loop through each genotype (CropParameterItem)
    for item in root.xpath('//CropParameterItem'):
        genotype = item.get('name')  # Get the name of the genotype
        # Loop through each parameter under ParamValue
        for param in item.xpath('ParamValue/Item'):
            key = param.xpath('Key/string')[0].text  # Parameter name
            value = float(param.xpath('Value/double')[0].text)  # Parameter value as float
            genotype_params[genotype][key] = value

    return genotype_params,tree
# Function to find common parameters across genotypes with the same value
def find_common_parameters(genotype_params):
    # Dictionary to track potential common parameters and their value
    common_params = {}

    # Get the list of all genotypes
    genotypes = list(genotype_params.keys())

    # Use the first genotype as a reference
    reference_genotype = genotypes[0]

    # Loop through all parameters of the reference genotype
    for param_key, param_value in genotype_params[reference_genotype].items():
        # Check if all other genotypes have the same value for this parameter
        if all(genotype_params[genotype].get(param_key) == param_value for genotype in genotypes):
            common_params[param_key] = param_value

    return common_params

def process_all_sqvarm_files(root_dir):
    result_dict = {}

    # Walk through the root directory and its subdirectories
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith('.sqvarm'):
                file_path = os.path.join(dirpath, filename)
                print(f"Processing: {file_path}")

                # Read the parameters for each genotype
                genotype_params, _ = read_genotype_parameters(file_path)

                # Find common parameters with the same value across all genotypes
                common_params = find_common_parameters(genotype_params)

                # Store the results in the result_dict using the filename (without extension) as the key
                file_key = os.path.splitext(os.path.basename(file_path))[0]
                result_dict[file_key] = common_params

    return result_dict

# Function to read the XML file, remove a specific parameter, and return the modified tree
def read_and_remove_parameter(file_path, param_to_remove):
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(file_path, parser)
    root = tree.getroot()

    # Loop through each genotype (CropParameterItem)
    for item in root.xpath('//CropParameterItem'):
        # Loop through each parameter under ParamValue and remove the one to delete
        for param in item.xpath('ParamValue/Item'):
            key = param.xpath('Key/string')[0].text  # Parameter name
            if key == param_to_remove:
                parent = param.getparent()
                parent.remove(param)
                break  # Assuming you only want to remove one instance

    return tree

# Function to convert the result dictionary to a DataFrame
def convert_result_to_df(result_dict):
    # Create a list of Series to concatenate later
    param_series_list = []

    # Iterate through the result dictionary and add each file's common parameters
    for file_name, common_params in result_dict.items():
        # Create a Series with the file name as the index
        param_series = pd.Series(common_params, name=file_name)
        param_series_list.append(param_series)

    # Concatenate all Series into a DataFrame
    df = pd.concat(param_series_list, axis=1).T

    # Reset index to make 'File' a column
    df.reset_index(inplace=True)
    df.rename(columns={'index': 'File'}, inplace=True)

    return df
# Function to subselect columns where all values are the same and there are no NA
def subselect_columns(df):
    # Filter columns where all values are the same and not NA
    same_value_columns = df.nunique().eq(1)  # Check for uniqueness
    no_na_columns = df.notna().all()         # Check for NA

    # Combine conditions to get the desired columns
    selected_columns = same_value_columns & no_na_columns

    # Subselect the DataFrame
    result_df = df.loc[:, selected_columns]

    return result_df

def create_excluded_columns_df(original_df, filtered_df):
    # Get the columns to exclude
    excluded_columns = filtered_df.columns

    # Create a new DataFrame with columns not in filtered_df
    excluded_df = original_df.drop(columns=excluded_columns, errors='ignore')

    return excluded_df

# Function to remove parameters from B that are not in A
def remove_extra_parameters_in_B(tree_B, params_A):
    root_B = tree_B.getroot()

    # Iterate through each genotype in file B
    for item in root_B.xpath('//CropParameterItem'):
        for param in item.xpath('ParamValue/Item'):
            key = param.xpath('Key/string')[0].text
            if key not in params_A[next(iter(params_A))]:  # If param not in A, remove it
                parent = param.getparent()
                parent.remove(param)

    return tree_B
# Function to add missing parameters from A to B with the average value from A
def add_missing_parameters_in_B(tree_B, avg_values_to_add):
    root_B = tree_B.getroot()

    # Iterate through each genotype in file B and add missing parameters
    for item in root_B.xpath('//CropParameterItem'):
        for param_name, avg_value in avg_values_to_add.items():
            # Check if the parameter is missing in the genotype
            existing_keys = {param.xpath('Key/string')[0].text for param in item.xpath('ParamValue/Item')}
            if param_name not in existing_keys:
                # Create a new parameter element and add it to the genotype
                new_param = etree.Element("Item")
                key = etree.SubElement(new_param, "Key")
                key_string = etree.SubElement(key, "string")
                key_string.text = param_name

                value = etree.SubElement(new_param, "Value")
                value_double = etree.SubElement(value, "double")
                value_double.text = str(avg_value)

                # Append the new parameter to the ParamValue section
                item.find('ParamValue').append(new_param)

    return tree_B

# Main function to process and sync files A and B
def sync_files_A_and_B(file_A, file_B, output_file_B):
    # Read parameters from both files
    params_A, _ = read_genotype_parameters(file_A)
    params_B, tree_B = read_genotype_parameters(file_B)

    # Remove parameters from B that are not in A
    modified_tree_B = remove_extra_parameters_in_B(tree_B, params_A)

    # Calculate the average values of parameters in A that need to be added to B
    avg_values_to_add = {}
    for param in (set(params_A[next(iter(params_A))].keys()) - set(params_B[next(iter(params_B))].keys())):
        avg_values_to_add[param] = sum(genotype[param] for genotype in params_A.values() if param in genotype) / len(params_A)

    # Add missing parameters to B from A
    modified_tree_B = add_missing_parameters_in_B(modified_tree_B, avg_values_to_add)

    # Rewrite the modified XML tree for B to the specified output file
    rewrite_xml(modified_tree_B, output_file_B)