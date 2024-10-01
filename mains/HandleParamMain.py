import os

import functions.HandleParam as HandleParam
import Constant





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