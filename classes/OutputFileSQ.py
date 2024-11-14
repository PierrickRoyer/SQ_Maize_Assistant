import xml.etree.ElementTree as ET
import os
import pandas as pd
import re
from collections import defaultdict


def default_str():
    return defaultdict(str)
class OutputFileSQ:
    def __init__(self, model_version, input_dir_path, name, extension):
        self.input_dir_path = input_dir_path
        self.file_path = os.path.join(input_dir_path, name + extension)  # Ensure correct file path
        self.name = name
        self.model_version = model_version

        base_parent_dir = os.path.basename(input_dir_path)
        parts = base_parent_dir.split('_')

        # Validate and assign DB_name, modeller_name, and original_model_version
        if len(parts) >= 4:
            self.DB_name = parts[0]
            self.modeller_name = parts[1]
            self.original_model_version = parts[2]


        else:
            raise ValueError("Directory name format is incorrect; expected 'DB_modeller_originalVersion_varietal_target_version'.")

    def parse_meta(self, data):
        # Split each line, remove ":" from keys, and create dictionary entries from key-value pairs
        self.meta = {line.split('\t', 1)[0].replace(':', '').strip(): line.split('\t', 1)[1].strip()
                     for line in data.strip().split('\n')}


class SummaryOutput(OutputFileSQ):
    def __init__(self, model_version, input_dir_path, name, extension):
        super().__init__(model_version, input_dir_path, name, extension)
        self.dailys = defaultdict(default_str)
        self.load_file()

    def load_file(self):
        with open(self.file_path, 'r') as file:
            content = file.read().split('\n\n')  # Split into parts by double newline

            if len(content) < 3:
                raise ValueError("File format is incorrect; expected three sections separated by double newlines.")

            # Assign each part to the corresponding key in the dictionary
            self.header = content[0],
            self.parse_meta(content[1])
            self.summ_data =  self.parse_data(content[2])  # Process data into a DataFrame

    def parse_data(self, data_section):
        # Split data section by lines and use the second line as column headers
        lines = data_section.strip().split('\n')

        # The first line might be a description or ignored, use the second line as column headers
        column_headers = lines[1].split('\t')
        data_rows = [line.split('\t') for line in lines[2:]]  # Data rows start after the column headers

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=column_headers)

        return df

    def link_daily(self,list_daily):

        for daily in list_daily:
            #print(daily.TRT_NAME,daily.CUL_ID,daily.pheno)
            self.dailys[daily.TRT_NAME][daily.CUL_ID] = daily


class DailyOutput(OutputFileSQ):
    def __init__(self, model_version, input_dir_path, name, extension):
        super().__init__(model_version, input_dir_path, name, extension)
        self.load_file()
        self.TRT_NAME = name.split('_')[-1]
        self.CUL_ID = '_'.join(self.name.split('_')[0:-1])

    def load_file(self):
        with open(self.file_path, 'r') as file:
            content = re.split(r'\n{2,}', file.read())  # Split into parts by double newline

            if len(content) < 4:
                raise ValueError("File format is incorrect; expected three sections separated by double newlines.")

            # Assign each part to the corresponding key in the dictionary
            self.header = content[0]
            self.parse_meta(content[1])
            self.pheno = self.parse_data(content[2],2)
            self.data =  self.parse_data(content[3],2)
            self.leaves = self.parse_data(content[4],1)

    def parse_data(self, data_section,column_headers_rank):
        # Split data section by lines and use the second line as column headers
        lines = data_section.strip().split('\n')

        # The first line might be a description or ignored, use the second line as column headers
        column_headers = lines[column_headers_rank].split('\t')
        data_rows = [line.split('\t') for line in lines[3:]]  # Data rows start after the column headers

        # Create DataFrame
        df = pd.DataFrame(data_rows, columns=column_headers)
        #print(df.columns)
        if 'SITE_NAME' in df.columns :
            self.SITE_NAME = df['SITE_NAME'].iloc[0]
        if 'EXNAME' in df.columns :
            self.EXNAME = df['EXNAME'].iloc[0]
        if 'SOIL_NAME' in df.columns :
            self.SOIL_NAME = df['SOIL_NAME'].iloc[0]

        return df

























