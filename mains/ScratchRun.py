import os
import subprocess
from concurrent.futures import ThreadPoolExecutor
SQpath = 'C:/Users/royerpie/Source\Repos/SiriusCode/Code/SiriusConsole/bin\Debug/SiriusQuality-Console.exe'
sqproPath = 'C:/Users/royerpie/Documents/rootDoc/Working_Immuable/myProject/cross/2.2.0/PG_Pierrick_2.0.0/1-Project/PG_Pierrick.sqpro'
os.system(SQpath +" -sim true true " + sqproPath + " --Run RUN_all")

def run_sirius_quality(run_argument):
    command = f"{SQpath} -sim true true {sqproPath} --Run {run_argument}"
    print(command)
    subprocess.Popen(command, shell=True)

# List of different --Run arguments
run_arguments = [ 'run_1', "RUN_all"]  # Add more as needed

# Execute the commands in parallel
with ThreadPoolExecutor() as executor:
    executor.map(run_sirius_quality, run_arguments)