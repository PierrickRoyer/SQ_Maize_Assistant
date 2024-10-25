import xml.etree.ElementTree as ET
import pandas as pd
import Constant

def parse_soil_xml(xml_file):
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Initialize lists for CSV output
    soil_info = []
    layer_info = []

    # Extract soil item attributes
    for soil_item in root.findall('.//SoilItem'):

        soil_id = soil_item.get('name', '')
        # Get general soil properties
        soil_name = soil_id  # You can replace this with a specific property if needed
        sl_dp = soil_item.find('BD').text if soil_item.find('BD') is not None else ''  # Placeholder for SLDP

        # Append soil info
        soil_info.append({
            'SOIL_ID': soil_id,
            'Soil_NAME': soil_name,
            'SLDP': sl_dp
        })

        # Extract layer data
        depth_start = 0
        for layer in soil_item.findall('.//SoilLayer'):
            depth_end = depth_start + float(layer.find('Depth').text) if layer.find('Depth') is not None else 0
            sllb = layer.find('Clay').text if layer.find('Clay') is not None else ''
            sllt = depth_start
            slsat = layer.find('SSAT').text if layer.find('SSAT') is not None else ''
            sldul = layer.find('SDUL').text if layer.find('SDUL') is not None else ''
            slll = layer.find('SLL').text if layer.find('SLL') is not None else ''
            slbdm = sl_dp  # You can modify this to extract the correct data
            slni = layer.find('Kql').text if layer.find('Kql') is not None else ''
            slcly = layer.find('Clay').text if layer.find('Clay') is not None else ''

            # Append layer info
            layer_info.append({
                'SOIL_ID': soil_id,
                'SLLT': sllt,
                'SLLB': sllb,
                'SLSAT': slsat,
                'SLDUL': sldul,
                'SLLL': slll,
                'SLBDM': slbdm,
                'SLNI': slni,
                'SLCLY': slcly
            })

            depth_start = depth_end  # Update the starting depth for the next layer

    # Create DataFrames from the lists
    df_soil = pd.DataFrame(soil_info)
    df_layers = pd.DataFrame(layer_info)

    return df_soil, df_layers

df_soilMeta,df_soilLayer = parse_soil_xml("C:/Users/royerpie/Documents/rootDoc/automate\currWork\All.sqsoi")
print(df_soilMeta)
df_soilLayer.to_csv(Constant.pathMyOutput + 'soilLayer_ALL_Lucille.csv')
print(df_soilLayer)
df_soilMeta.to_csv(Constant.pathMyOutput + 'soilMeta_ALL_Lucille.csv')