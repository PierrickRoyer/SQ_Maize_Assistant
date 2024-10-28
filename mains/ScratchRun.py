import os
import subprocess
from concurrent.futures import ThreadPoolExecutor

sqproPath = 'C:/Users/royerpie/Documents/rootDoc/Working_Immuable/myProject/cross/2.2.0/PG_Pierrick_2.0.0/1-Project/PG_Pierrick.sqpro'


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



run_arguments = ['run_1', 'RUN_all']
execute_parallel_runs(SQpath, sqproPath, run_arguments)