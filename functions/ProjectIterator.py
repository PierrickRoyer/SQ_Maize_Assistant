import shutil
from classes.InputFileSQ import *
from classes.OutputFileSQ import *
import subprocess
from concurrent.futures import ThreadPoolExecutor
from collections import defaultdict

def iterate_over_project_input(root_dir):

    model_version = os.path.basename(root_dir)
    projects = list()
    varieties = list()
    runs = list()
    # Traverse through the main directory and subdirectories
    for base, dirs, files in os.walk(root_dir):
        # Check if we're in a `1-Project` directory
        if os.path.basename(base) == "1-Project":
            # Extract the parent directory name to get DatabaseName, ModellerName, and version
            parent_dir_name = os.path.basename(os.path.dirname(base))
            print(parent_dir_name)

            # Initialize empty dictionaries for each project type found


            # Find the `.sqpro`, `.sqvar`, and `.sqrun` files in this directory
            for file in files:
                file_path = os.path.join(base, file)

                if file.endswith('.sqpro'):
                    print(file_path)
                    # Initialize a Project object
                    project = Project(model_version, base, file.replace('.sqpro', ''), '.sqpro')

                    projects.append(project)

                elif file.endswith('.sqvarm'):
                    # Initialize a Variety object
                    variety = Variety(model_version, base, file.replace('.sqvarm', ''), '.sqvarm')
                    varieties.append(variety)

                elif file.endswith('.sqrun'):
                    # Initialize a Run object
                    run = Run(model_version, base, file.replace('.sqrun', ''), '.sqrun')
                    runs.append(run)

    return  projects, varieties, runs




def run_sirius_quality(SQpath, sqproPath, run_argument):
    """Function to run SiriusQuality with specified paths and --Run argument."""
    command = f"{SQpath} -sim true true {sqproPath} --Run {run_argument}"
    print(f"Executing: {command}")

    # Using subprocess.run to wait for each command to complete
    result = subprocess.run(command, shell=True)

    # Check for any errors
    if result.returncode != 0:
        print(f"Error running command: {command}")


def execute_parallel_runs(SQpath, sqproPath, run_arguments):
    """Execute multiple SiriusQuality runs in parallel using provided paths and run arguments."""
    with ThreadPoolExecutor() as executor:
        executor.map(lambda run_arg: run_sirius_quality(SQpath, sqproPath, run_arg), run_arguments)


def check_and_clean_dir(dir_path):
    """Check if a directory exists. If it does, clean its contents. If not, create it."""
    # Check if the directory exists
    if os.path.exists(dir_path):
        # If it exists, clear its contents
        for item in os.listdir(dir_path):
            item_path = os.path.join(dir_path, item)
            # Remove files or directories
            if os.path.isfile(item_path) or os.path.islink(item_path):
                os.remove(item_path)
                #print(f"Removed file: {item_path}")
            elif os.path.isdir(item_path):
                shutil.rmtree(item_path)
                print(f"Removed directory: {item_path}")
        print(f"Cleaned existing directory: {dir_path}")
    else:
        # If it doesn't exist, create it
        os.makedirs(dir_path)
        print(f"Created new directory: {dir_path}")

def remove_files_with_substring(directory, substring):
    """Walks through a directory and removes all files containing a specific substring in their name."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            if substring in file:
                file_path = os.path.join(root, file)
                try:
                    os.remove(file_path)
                    print(f"Removed: {file_path}")
                except Exception as e:
                    print(f"Error removing {file_path}: {e}")


def concatenate_sirius_quality_files(input_files, output_file):
    header = []
    column_headers = []
    data_lines = []
    first_file = True

    # Loop through each file in the input files list
    for file_path in input_files:
        with open(file_path, 'r') as file:
            lines = file.readlines()

            # For the first file, store the header and column definitions
            if first_file:
                header = lines[:15]
                column_headers = lines[15:17]
                first_file = False

            # Append only the data lines (after line 17)
            data_lines.extend(lines[17:])

    # Write everything to the output file
    with open(output_file, 'w') as output:
        output.writelines(header)  # Write the header once
        output.writelines(column_headers)  # Write column headers once
        output.writelines(data_lines)  # Write all concatenated data


def iterate_over_project_output(root_dir):
    model_version = os.path.basename(root_dir)
    output = defaultdict(dict)

    for base, dirs, files in os.walk(root_dir):
        # Check if we're in a `3-Output` directory
        if os.path.basename(os.path.dirname(base)) == "3-Output":
            run_name = os.path.basename(base)
            print(run_name)
            output[run_name] = {
                'Summary': None,  # Initialize Summary key for each run
                'Daily': []  # Initialize Daily key as a list
            }
            # Gather all `.sqbrs` files in this directory
            sqbrs_files = [os.path.join(base, file) for file in files if file.endswith('.sqbrs')]

            if sqbrs_files and f"{run_name}_summary.sqbrs" not in files:
                # Define the path for the concatenated output file
                concatenated_file_path = os.path.join(base, f"{run_name}_summary.sqbrs")

                # Run the concatenation function
                concatenate_sirius_quality_files(sqbrs_files, concatenated_file_path)

            if sqbrs_files:

                # Create a single SummaryOutput object with the concatenated file
                summ = SummaryOutput(model_version, base, f"{run_name}_summary", '.sqbrs')
                output[run_name]['Summary'] = summ

            # Process `.sqsro` files as DailyOutput objects
            for file in files:
                if file.endswith('.sqsro'):
                    day = DailyOutput(model_version, base, file.replace('.sqsro', ''), '.sqsro')
                    output[run_name]['Daily'].append(day)

    return output