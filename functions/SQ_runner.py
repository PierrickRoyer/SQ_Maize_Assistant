import os
root_modele_path = "C:/Users/royerpie/Documents/rootDoc/automate/modeles/"


SQpath = 'C:/Users/royerpie/Documents/Work/Script/SiriusCode/Code/SiriusConsole/bin/Debug/SiriusQuality-Console.exe'
sqproPath = 'C:/Users/royerpie/Documents/Work/Return/mySQthirdTimeTheCharm/1-Project/again.sqpro'
os.system(SQpath +" -sim true true " + sqproPath + " --Run 5_CAR")