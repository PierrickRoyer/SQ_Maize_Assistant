import shutil
from classes.InputFileSQ import *
import subprocess
from concurrent.futures import ThreadPoolExecutor


def iterate_over_project(root_dir):

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
 # Remove directory

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