import os
from classes.InputFileSQ import *



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
