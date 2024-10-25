import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from collections import defaultdict
import functions.HandleParam as HandleParam
import Constant
from functions.HandleParam import extract_parameters_to_df

##Get potential non-var Param
"""
result_dict = HandleParam.process_all_sqvarm_files(Constant.pathParameters)

# Convert the result dictionary to a DataFrame
df = HandleParam.convert_result_to_df(result_dict)
filtered_df = HandleParam.subselect_columns(df)
excluded_df =  HandleParam.create_excluded_columns_df(df,filtered_df)
# Display the DataFrame
print(df)

excluded_df = excluded_df.transpose()
#excluded_df.to_csv( Constant.pathMyOutput + '\compareParam/potentialNonVarietal_Param_PG_INVITE.csv', sep =';')

filtered_df = filtered_df.transpose()
#filtered_df.to_csv(Constant.pathMyOutput + '\compareParam/constantNonVarietalParam_PG_INVITE.csv', sep =';')
"""


        ##Delete Param
""""
dirpath = "C:/Users/royerpie/Documents/rootDoc/backup_Immuable/myProject/reproduce/INVITE_Jugurta_2.1.2/1-Project/"
for file in os.listdir(dirpath):
    if file.endswith("sqvarm"):
        file_path = os.path.join(dirpath, file)
        tree = HandleParam.read_and_remove_parameter(file_path,'stopLigul')
        HandleParam.rewrite_xml(tree,file_path)


"""
    ##Edit Param for specific version
"""
targetVersion = '2.2.0'
sqvarmRef = os.path.join(Constant.pathParameters, 'PG_2.1.2', 'PG_Jugurta_2.1.2.sqvarm')
sqvarmToEditDir = os.path.join(Constant.pathParameters, 'all_working_reproduction')
logDir = os.path.join(sqvarmToEditDir,targetVersion, 'log')

# Iterate through all files in the directory
for file in os.listdir(sqvarmToEditDir):
    if file.endswith('sqvarm'):
        sqVarmEdited = file[:-7] + '_' + targetVersion
        logFile = os.path.join(logDir, f'{sqVarmEdited}_log.txt')
        sqvarmEdit = os.path.join(sqvarmToEditDir, file)
        outputFile = os.path.join(sqvarmToEditDir, targetVersion, f'{sqVarmEdited}.sqvarm')

        # Ensure log directory exists
        os.makedirs(logDir, exist_ok=True)

        # Call the function to sync and log
        HandleParam.sync_files_A_and_B(sqvarmRef, sqvarmEdit, outputFile, logFile, targetVersion)
"""
file =  "C:/Users/royerpie/Documents/rootDoc/automate/parameters/Lucille_1.1.sqvarm"
sqvarmRef = os.path.join(Constant.pathParameters, 'PG_2.1.2', 'PG_Jugurta_2.1.2.sqvarm')
logFile = 'none'
targetVersion = '2.2.0'

outputFile = "C:/Users/royerpie/Documents/rootDoc/automate/parameters/Lucilel_1.1_2.2.0.sqvarm"

HandleParam.sync_files_A_and_B(sqvarmRef, file, outputFile, logFile, targetVersion)
    ##Generate sqvarm and sqparm from EXCEL
"""
sqvarm = pd.read_excel(Constant.pathParameters + 'Lucille_1.1/param_var_all.xlsx')
sqvarm.rename(columns={'Unnamed: 0': 'Parameter'}, inplace=True)
print(sqvarm)
sqvarm = HandleParam.generate_param(sqvarm,Constant.pathParameters + '/Lucille_1.1/generatedParamVarAllNew.sqvarm','variety')
"""
    ##compare & align Param Among Version
"""
sq_dir = Constant.pathParameters + 'all_working_reproduction/'
sqvarm_ref_file = sq_dir + 'APEX_1.0.0.sqvarm'
sqparm_ref_file = sq_dir + 'APEX_1.0.0.sqparm'
groboudin = defaultdict(dict)
for file in os.listdir(sq_dir):

    temp = HandleParam.extract_parameters_to_df(os.path.join(sq_dir,file))
    #print(temp)
    groboudin[file[:-6]] = temp
#print("groboudin",groboudin)
summary_df = HandleParam.consolidate_dfs_and_calculate_avg(groboudin)
print("summary",summary_df)
summary_df.to_csv("opaniPue.csv")
#summary_df.to_csv(Constant.pathMyOutput + 'tryCompareparam.csv')
# Colorize the summary DataFrame

#print(styled_summary_df)
output_file = 'summary_with_colors.xlsx'
with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
    summary_df.to_excel(writer, sheet_name='Summary', startrow=0)

    # Apply colors to the Excel sheet
    HandleParam.apply_color_to_excel(writer, summary_df)
"""
"""
sqparm = pd.read_excel(Constant.pathParameters + 'Lucille_1.1/nonVar_PM.xlsx')
print(sqparm)
sqparm = HandleParam.generate_param(sqparm, Constant.pathParameters + '/Lucille_1.1/generatedNonVar2.sqparm',False)

sqparm = pd.read_excel(Constant.pathParameters + 'Lucille_1.1/nonVar_PM.xlsx')
xml_file_path = Constant.pathParameters + '/Lucille_1.1/NonVarietal_20160201maizeOld.sqparm'
output_file_path = Constant.pathParameters + '/Lucille_1.1/editOldGenerationThisWillWork.sqparm'
HandleParam.sync_non_variety_file_with_df(xml_file_path, sqparm, output_file_path)

HandleParam.sync_non_variety_files(Constant.pathParameters + "Lucille_1.1/NonVarietal_20160201maizeOld.sqparm",
                                   Constant.pathParameters + "Lucille_1.1/NonVarietal_20160201maize.sqparm",
                                   Constant.pathParameters + "Lucille_1.1/NonVarNewWithOldList.sqparm",
                                   Constant.pathParameters + "prout'" )
"""

"""

sqvarm_df = HandleParam.collect_sqvarm_data(Constant.pathParameters)
recap_df = HandleParam.compare_sqvarm_files(sqvarm_df)

# Save the recap as a CSV
recap_df.to_csv(os.path.join(Constant.pathParameters, 'recap_parameters.csv'), index=False, sep = ';')
"""
## add all apram to sqvarm
"""
HandleParam.add_sqparm_to_sqvarm("C:/Users/royerpie/Documents/rootDoc/automate/parameters/Lucille_1.1/ParametersVarAll.sqvarm",
                                 "C:/Users/royerpie/Documents/rootDoc/automate/parameters/Lucille_1.1/NonVarietal_20160201maize_EB.sqparm",
                                 "C:/Users/royerpie/Documents/rootDoc/automate/parameters/Lucille_1.1.sqvarm")
"""