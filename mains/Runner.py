from Constant import pathProjectCross
from classes.InputFileSQ import Project, Run, Variety
import functions.ProjectIterator as ProjectIterator
import os
"""
project_path =os.path.join( pathProjectCross , "2.2.0","PG_Pierrick_2.0.0","1-Project")
print(project_path)
print(os.path.basename(project_path))

projet_test =Project("2.2.0",project_path, "PG_Pierrick",".sqpro")
projet_test.execute()

projet_test.files['RunFileName'] = 'ducacapourmesgarssur'
print(projet_test.files)
projet_test.save_xml(project_path + 'propopote.sqpro')


run_test = Run("2.2.0",project_path, "PG_Pierrick",".sqrun")
run_test.runs.pop('run_1')

print(run_test.group_runs_by_site_item())
run_test.execute()
run_test.save_xml('test.sqrun')

var_test = Variety("2.2.0",project_path, "PG_2.0.0_2.2.0",".sqvarm")
var_test.execute()
print(var_test.DB_name)


print(projet_test.DB_name)
print(run_test.DB_name)
"""

model_version = "2.2.0"
project_path =os.path.join( pathProjectCross , model_version)

pro,var,run = ProjectIterator.iterate_over_project(project_path)
print(pro)
for project in pro :
    print(project.DB_name,project.modeller_name,project.original_model_version)
print('==')
for variety in var:
    print(variety.DB_name,variety.modeller_name,variety.original_model_version, variety.name)
print('==')
print('==')
for r in run:
    r.split_RUN_all_by_site()
    print(r.DB_name, r.modeller_name, r.original_model_version, r.name)
    for multi in r.runs:
        print(multi)