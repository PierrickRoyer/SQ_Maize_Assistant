import xml.etree.ElementTree as ET
import pandas as pd
import Constant

def parse_xml(xml_file):
    # Parse the XML file
    tree = ET.parse(xml_file)
    root = tree.getroot()


    # Define the columns for the DataFrames
    planting_data = []
    dataWater = {'EID': [], 'TREAT_ID': [], 'IDATE': [], 'IRVAL': []}
    dataNitro = {'EID': [], 'TREAT_ID': [], 'FEDATE': [], 'FEAMN': []}

    # Iterate over each ManagementItem in the XML
    for item in root.findall('.//ManagementItem'):
        print('hereManage')
        experiment_name = item.find('ExperimentName').text if item.find('ExperimentName') is not None else ''
        treatment_name = item.get('name')  # Assumes 'name' attribute is the TREAT_ID
        sowing_date = item.find('SowingDate').text.split('T')[0] if item.find('SowingDate') is not None else ''
        sowing_density = item.find('SowingDensity').text if item.find('SowingDensity') is not None else ''

        # Create a dictionary for the planting row
        planting_row = {
            "EID": experiment_name,
            "TREAT_ID": treatment_name,
            "PDATE": sowing_date,
            "PLPOP": sowing_density,
            "APLDAE": '',  # These can remain blank
            "APLPOE": '',
            "SDAT": '',
            "PL_NOTES": ''
        }

        planting_data.append(planting_row)

        # Iterate over DateApplications within the ManagementItem
        for date_app in item.findall(".//DateApplication"):
            print('hereApply')
            TREAT_ID = treatment_name
            date = date_app.find('Date').text.split('T')[0]  # Extract only the date part

            water_mm = date_app.find('WaterMM')
            nitrogen = date_app.find('Nitrogen')

            # Add water data if WaterMM is present
            if water_mm is not None:
                dataWater['EID'].append(treatment_name[:-2])  # Adjust EID format if necessary
                dataWater['TREAT_ID'].append(TREAT_ID)
                dataWater['IDATE'].append(date)
                dataWater['IRVAL'].append(water_mm.text)

            # Add nitrogen data if Nitrogen is present
            if nitrogen is not None:
                dataNitro['EID'].append(treatment_name)
                dataNitro['TREAT_ID'].append(TREAT_ID)
                dataNitro['FEDATE'].append(date)
                dataNitro['FEAMN'].append(nitrogen.text)

    print(planting_data)
    print(dataWater)
    # Convert lists/dictionaries to DataFrames
    df_planting = pd.DataFrame(planting_data)

    dfWater = pd.DataFrame(dataWater)
    dfNitro = pd.DataFrame(dataNitro)

    return df_planting, dfWater, dfNitro


def parse_management_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # List to store planting data rows
    planting_data = []

    # Iterate over each ManagementItem in the XML
    for item in root.findall('.//ManagementItem'):
        experiment_name = item.find('ExperimentName').text if item.find('ExperimentName') is not None else ''
        treatment_name = item.get('name')  # Assumes 'name' attribute is the TREAT_ID
        sowing_date = item.find('SowingDate').text.split('T')[0] if item.find('SowingDate') is not None else ''
        sowing_density = item.find('SowingDensity').text if item.find('SowingDensity') is not None else ''

        # Create a dictionary for the planting row with blanks for missing fields
        planting_row = {
            "EID": experiment_name,
            "TREAT_ID": treatment_name,
            "PDATE": sowing_date,
            "PLPOP": sowing_density,
            "APLDAE": '',  # These can remain blank
            "APLPOE": '',
            "SDAT": '',
            "PL_NOTES": ''
        }

        planting_data.append(planting_row)

    # Convert to DataFrame
    df_planting = pd.DataFrame(planting_data)

    return df_planting

def parse_manage_nitro_water(xml_file):

    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Define the columns for the DataFrame
    dataWater = {'EID': [], 'TREAT_ID': [], 'IDATE': [], 'IRVAL': []}
    dataNitro = {'EID': [], 'TREAT_ID': [], 'FEDATE': [], 'FEAMN': []}
    # Iterate over each ManagementItem and extract relevant DateApplications
    for item in root.findall(".//ManagementItem"):
        EID = item.find('ExperimentName').text if item.find('ExperimentName') is not None else ''
        TREAT_ID = item.get('name')  # Assumes 'name' attribute is the TREAT_ID
        print(EID)
        for date_app in item.findall(".//DateApplication"):
            print('EID', EID)  # Get the 'name' attribute for EID

            print(TREAT_ID)  # You can define TREAT_ID if available in the XML
            nitrogen = date_app.find('Nitrogen').text
            water_mm = date_app.find('WaterMM').text
            date = date_app.find('Date').text.split('T')[0]  # Extract only the date part

            # Add the data to the DataFrame dictionary
            dataWater['EID'].append(EID)
            dataWater['TREAT_ID'].append(TREAT_ID)
            dataWater['IDATE'].append(date)
            dataWater['IRVAL'].append(water_mm)

            dataNitro['EID'].append(EID)
            dataNitro['TREAT_ID'].append(TREAT_ID)
            dataNitro['FEDATE'].append(date)
            dataNitro['FEAMN'].append(nitrogen)

    # Convert to DataFrame
    df = pd.DataFrame(dataWater)
    df2 = pd.DataFrame(dataNitro)

    return df,df2
# Load and parse the XML file
xml_file = "C:/Users/royerpie/Documents/rootDoc/automate\currWork\All.sqman"  # Change this to the path of your XML file

dfPlanting = parse_management_xml(xml_file)
dfWater,dfNitro = parse_manage_nitro_water(xml_file)
print(dfWater,dfNitro)
print(dfPlanting)

dfPlanting.to_csv(Constant.pathMyOutput + 'planting_ALL_Lucille.csv')
dfNitro.to_csv(Constant.pathMyOutput + 'nitro_ALL_Lucille.csv')
dfWater.to_csv(Constant.pathMyOutput + 'water_ALL_Lucille.csv')