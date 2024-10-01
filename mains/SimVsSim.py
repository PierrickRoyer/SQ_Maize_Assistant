import functions.LoadTransform as LoadTransform
import functions.Compare as Compare
import Constant
import pandas as pd

from functions.LoadTransform import load_sim_summ_SQ


    ##compare INVITE / Jugurta 2.1.1 (theorically  works for PG)

"""
myArva_Ju_2_1_1 = LoadTransform.load_sim_summ_csv(Constant.pathMyOutput + 'Invite_Jugurta_2.1.1/ARVA_1.csv',';', 'RUID', 'latin1')
oldArva_Ju_2_1_1 = LoadTransform.load_Jugurta_arborescence(Constant.pathOldOutput + 'Invite_Jugurta_2.1.1\output_Arva_1/','RUID', 'latin1' )
oldArva_Ju_2_1_1.to_csv(Constant.pathOldOutput + 'Invite_Jugurta_2.1.1/output_Arva_1/Arva_1.csv', sep = ';')
print(oldArva_Ju_2_1_1[['ADAT','MDAT']])
oldArva_Ju_2_1_1 = LoadTransform.convert_date_columns(oldArva_Ju_2_1_1,'%Y-%m-%d')
myArva_Ju_2_1_1 = LoadTransform.convert_date_columns(myArva_Ju_2_1_1,'%d/%m/%Y')
print(myArva_Ju_2_1_1[['ADAT','MDAT']])

outputDF = Compare.compare_sim_vs_sim_list(oldArva_Ju_2_1_1,myArva_Ju_2_1_1,'oldJugu','newPierrick',Constant.varJugurta,['RUID','TRT_NAME'])
outputDF.to_csv(Constant.pathSimvsSimOutput + 'Invite_Jugurta_2.1.1/ARVA_2.csv', sep =';')
"""

    ##compare PG / Pierrick 2.0.0

old = pd.read_csv("C:/Users/royerpie/Documents/rootDoc/results/simVsSimDf/PG_Pierrick_old.csv", sep = ';', encoding = 'latin1')
print(old[['PDATE', 'ADAT', 'MDAT']])
old = LoadTransform.convert_date_columns(old, '%d/%m/%Y')
print(old[['PDATE', 'ADAT', 'MDAT']])
new =LoadTransform.load_sim_summ_csv("C:/Users/royerpie/Documents/rootDoc/automate/myOutput/PG_Pierrick_2.0.0\PG_reversed.csv", ';','RUID','latin1')
new = LoadTransform.convert_date_columns(new, '%d/%m/%Y')
print(new[['PDATE', 'ADAT', 'MDAT']])

outputDF = Compare.compare_sim_vs_sim_list(old, new, 'old','new', ['ADAT','MDAT','LAIX'], ['TRT_NAME','CUL_ID'])
outputDF.to_csv(Constant.pathSimvsSimOutput + 'PG_pierrick_reversed.csv', sep =';')




    ##compare PG / Jugurta 2.1.1
"""
currPathNewOutput = Constant.pathMyOutput + 'PG_Jugurta_2.1.1/PG_Jugurta_1_edit.csv'
currPathOldOutput = Constant.pathOldOutput + 'PG_Jugurta_2.1.1\output_PG_Jugurta_1/'
currPathSimVsSim =  Constant.pathSimvsSimOutput + 'PG_Jugurta_2.1.1/'

new = LoadTransform.load_sim_summ_csv(currPathNewOutput,';', 'RUID', 'latin1')

old = LoadTransform.load_Jugurta_arborescence(currPathOldOutput,'RUID', 'latin1' )
print(old['ADAT'])

old = LoadTransform.convert_date_columns(old, '%Y-%m-%d')
#old.to_csv( Constant.pathOldOutput + 'PG_Jugurta_2.1.1\output_PG_Jugurta_1/summary_PG_1_Jugurta.csv', sep =';')
print(old['ADAT'])
print('here')
print(new['ADAT'])
new = LoadTransform.convert_date_columns(new, '%d/%m/%Y')

#print(myArva_Ju_2_1_1[['ADAT','MDAT']])

outputDF = Compare.compare_sim_vs_sim_list(old,new,'oldJugu','newPierrick',Constant.varJugurta,['RUID','TRT_NAME'])
outputDF.to_csv(currPathSimVsSim + 'PG_Jugurta_1.csv', sep =';')
"""