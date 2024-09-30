import xml.etree.ElementTree as ET
import pandas as pd

# Load and parse the XML file
xml_file = "C:/Users/royerpie/Documents/rootDoc/automate\project/2.0\PG/1-PG_Old_Pierrick/allPlusOne.sqman"  # Change this to the path of your XML file
tree = ET.parse(xml_file)
root = tree.getroot()

# Define the columns for the DataFrame
dataWater = {'EID': [], 'TREAT_ID': [], 'IDATE': [], 'IRVAL': []}
dataNitro = {'EID': [], 'TREAT_ID': [], 'FEDATE': [], 'FEAMN': []}
# Iterate over each ManagementItem and extract relevant DateApplications
for item in root.findall(".//ManagementItem"):
    EID = item.attrib.get('name', '')

    if '20' in EID and len(EID) > 2:
        for date_app in item.findall(".//DateApplication"):
            print('EID', EID[:-2])  # Get the 'name' attribute for EID
            TREAT_ID = EID
            print(TREAT_ID)  # You can define TREAT_ID if available in the XML
            nitrogen = date_app.find('Nitrogen').text
            water_mm = date_app.find('WaterMM').text
            date = date_app.find('Date').text.split('T')[0]  # Extract only the date part

            # Add the data to the DataFrame dictionary
            dataWater['EID'].append(EID[:-2])
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
# Save to CSV
print(df)
df.to_csv("C:/Users/royerpie/Documents/rootDoc/automate/myOutput/waterApply.csv")
print(df2)
df2.to_csv("C:/Users/royerpie/Documents/rootDoc/automate/myOutput/nitroApply.csv")