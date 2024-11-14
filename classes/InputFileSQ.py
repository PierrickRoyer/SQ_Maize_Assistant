import xml.etree.ElementTree as ET
import os
import pandas as pd


class InputFileSQ:
    def __init__(self, model_version, input_dir_path, name, extension):
        self.input_dir_path = input_dir_path
        self.xml_file_path = os.path.join(input_dir_path, name + extension)  # Ensure correct file path
        self.name = name
        self.model_version = model_version
        self.xml_tree = self.load_xml()

        # Extract base directory name and split parts
        base_parent_dir = os.path.basename(os.path.dirname(input_dir_path))
        parts = base_parent_dir.split('_')

        # Validate and assign DB_name, modeller_name, and original_model_version
        if len(parts) >= 3:
            self.DB_name = parts[0]
            self.modeller_name = parts[1]
            self.original_model_version = parts[2]
        else:
            raise ValueError(
                "Directory name format is incorrect; expected 'DB_modeller_originalSQversion'. "
                f"Got '{base_parent_dir}' with parts: {parts}"
            )

    def load_xml(self):
        """Load the XML file, with error handling for file-not-found or invalid XML formats."""
        try:
            # Attempt to parse the XML file
            tree = ET.parse(self.xml_file_path)
            return tree
        except FileNotFoundError:
            raise FileNotFoundError(f"XML file not found at path: {self.xml_file_path}")
        except ET.ParseError:
            raise ET.ParseError(f"Failed to parse XML file at path: {self.xml_file_path}. "
                                "The file may be improperly formatted.")

    def rewrite_xml(self, output_file):
        """Rewrite the XML file with a specific declaration format."""
        with open(output_file, 'wb') as f:
            # Manually write the XML declaration without encoding
            f.write(b'<?xml version="1.0"?>\n')
            # Write the rest of the XML tree without specifying encoding
            self.xml_tree.write(f, encoding='utf-8', xml_declaration=False)

class Project(InputFileSQ):
    def __init__(self, model_version, input_dir_path, name, extension = '.sqpro'):
        # Initialize the parent class (InputFileSQ)
        super().__init__(model_version, input_dir_path, name, extension)
        self.files = self.parse_xml()  # Call to parse_xml() after initializing parent class

    def parse_xml(self):
        """Parse XML data for Project, with error handling for missing elements."""
        try:
            root = self.xml_tree.getroot()
            inputs_element = root.find('Inputs')

            if inputs_element is None:
                raise ValueError(f"Missing 'Inputs' element in the XML file: {self.xml_file_path}")

            # Create a dictionary for each child element of `Inputs`
            self.files = {child.tag: child.text for child in inputs_element if child.text != '?'}
            return self.files
        except AttributeError:
            raise AttributeError(f"Failed to parse XML structure in file: {self.xml_file_path}. "
                                 "Ensure the XML format matches the expected schema.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while parsing the XML in Project: {e}")

    def execute(self):
        """Run the project logic."""
        print("Executing project with the following inputs:")
        self.display_inputs()

    def display_inputs(self):
        """Display parsed inputs."""
        for key, value in self.files.items():
            print(f"{key}: {value}")

    def load_normalized(self, list_to_load, root_dir):
        for i in list_to_load:
            extension = self.files[i].split('.')[-1]  # Get the file extension from self.files[i]

            # Search through root_dir for a file that matches the extension
            for file in os.listdir(root_dir):
                if file.endswith(extension):
                    # Set self.files[i] to the absolute path of the found file
                    self.files[i] = f"..\\..\\{file}"
                    break


    def save_xml(self, output_file):
        """Save the Project XML file with the current values in `self.files`."""
        # Create the root element
        root = ET.Element('ProjectFile')

        # Create the Inputs element
        inputs_elem = ET.SubElement(root, 'Inputs')

        # Add each item in `self.files` as a child element of Inputs
        for key, value in self.files.items():
            child_elem = ET.SubElement(inputs_elem, key)
            child_elem.text = str(value)

        # Create an ElementTree from the root and write to the file
        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

        # Read and modify to ensure no unwanted XML declaration
        with open(output_file, 'r', encoding='utf-8') as file:
            content = file.read()

        # Remove any unwanted XML declaration if necessary
        if content.startswith("<?xml version='1.0' encoding='utf-8'?>"):
            content = content.replace("<?xml version='1.0' encoding='utf-8'?>", "")

        # Save the modified content back
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(content)

class Run(InputFileSQ):
    def __init__(self, model_version, input_dir_path, name, extension = '.sqrun'):
        # Initialize the parent class (InputFileSQ)
        super().__init__(model_version, input_dir_path, name, extension)
        self.runs = self.parse_xml()  # Initialize runs attribute by parsing XML

    def parse_xml(self):
        """Parse XML data for Run, with error handling for missing or malformed elements."""
        try:
            root = self.xml_tree.getroot()
            runs_data = {}

            # Look for RunItem elements
            run_items = root.findall('.//RunItem')
            if not run_items:
                raise ValueError(f"No 'RunItem' elements found in the XML file: {self.xml_file_path}")

            for run_item in run_items:
                run_name = run_item.get('name')
                if run_name is None:
                    raise ValueError(f"RunItem missing 'name' attribute in XML file: {self.xml_file_path}")

                run_values = []

                # Process each MultiRunItem under the Multi tag
                multi_element = run_item.find('Multi')
                if multi_element is not None:
                    for multiItem in multi_element.findall('.//MultiRunItem'):
                        value = {gchild.tag: gchild.text for gchild in multiItem if gchild.text != '?'}
                        run_values.append(value)
                else:
                    raise ValueError(f"RunItem '{run_name}' is missing the 'Multi' element in XML file: {self.xml_file_path}")

                # Convert list of dictionaries to a DataFrame and store in runs_data
                runs_data[run_name] = pd.DataFrame(run_values)

            return runs_data
        except AttributeError:
            raise AttributeError(f"Failed to parse XML structure in file: {self.xml_file_path}. "
                                 "Ensure the XML format matches the expected schema.")
        except Exception as e:
            raise RuntimeError(f"An error occurred while parsing the XML in Run: {e}")

    def execute(self):
        """Run the project logic."""
        print("Executing run with the following inputs:")
        self.display_inputs()


    def display_inputs(self):
        """Display parsed inputs."""
        for key, value in self.runs.items():
            print(f"{key}: {value}")

    def split_RUN_all_by_site(self):

        keys_to_remove = [key for key in self.runs if key != 'RUN_all']

        # Remove all keys except 'name'
        for key in keys_to_remove:
            self.runs.pop(key)
        """Group runs by SiteItem and create separate DataFrames for each group."""
        grouped_runs = {}

        for run_name, df in self.runs.items():
            # Group by ManagementItem
            for site_item, group_df in df.groupby('SiteItem'):
                # Create a new RunItem for each ManagementItem
                grouped_runs[f"{site_item}"] = group_df.reset_index(drop=True)
        self.runs = grouped_runs
        return grouped_runs  # Return the grouped runs

    def create_run_file_element(self,output_run_dir):
        """Create the root RunFile element."""
        run_file_elem = ET.Element('RunFile')

        # Create ItemsArray element
        items_array_elem = ET.SubElement(run_file_elem, 'ItemsArray')

        # Loop through self.runs to create RunItems
        for run_name, df in self.runs.items():
            run_item_elem = ET.SubElement(items_array_elem, 'RunItem', attrib={'name': run_name})

            # Create Multi element
            multi_elem = ET.SubElement(run_item_elem, 'Multi')

            # Fill in the OutputDirectory and OutputPattern based on self.xml_tree (as an example)
            output_directory_elem = ET.SubElement(multi_elem, 'OutputDirectory')
            output_directory_elem.text = output_run_dir  # Adjust as needed

            output_pattern_elem = ET.SubElement(multi_elem, 'OutputPattern')
            output_pattern_elem.text = run_name  # Adjust as needed

            # Create MultiRunsArray element
            multi_runs_array_elem = ET.SubElement(multi_elem, 'MultiRunsArray')

            # Iterate over DataFrame rows and create MultiRunItem elements
            for _, row in df.iterrows():
                multi_run_item_elem = ET.SubElement(multi_runs_array_elem, 'MultiRunItem')

                # For each row, create sub-elements with the tag as the column and the text as the value
                for col, value in row.items():
                    sub_elem = ET.SubElement(multi_run_item_elem, col)
                    sub_elem.text = str(value)
            dailyoutput_directory_elem = ET.SubElement(multi_elem, 'DailyOutputPattern')
            dailyoutput_directory_elem.text = "$(VarietyName)_$(ManagementName)"  # Adjust as needed
        return run_file_elem

    def save_xml(self, output_file,output_run_dir):
        """Save the newly created XML structure."""
        root = self.create_run_file_element(output_run_dir)  # Create the new root element
        tree = ET.ElementTree(root)  # Create an ElementTree object

        # Write the XML tree to a file with the correct formatting
        tree.write(output_file, encoding='utf-8', xml_declaration=True)


class Variety(InputFileSQ):
    def __init__(self, model_version, input_dir_path, name, extension):
        super().__init__(model_version, input_dir_path, name, extension)
        self.parameters = self.parse_xml()  # Initialize runs attribute by parsing XML

    def parse_xml(self):
        root = self.load_xml()  # Load the XML data
        param_list = []  # List to hold dictionaries for each CropParameterItem

        for crop_param_item in root.findall('.//CropParameterItem'):
            run_values = {}  # Dictionary to hold parameters for the current CropParameterItem
            run_name = crop_param_item.get('name')  # Get the name attribute

            # Iterate over the ParamValue to collect parameter keys and values
            for param_value in crop_param_item.findall('.//ParamValue'):
                for item in param_value.findall('.//Item'):
                    key = item.find('./Key/string').text  # Extract the parameter key
                    value = item.find('./Value/double').text  # Extract the parameter value
                    run_values[key] = float(value) if value is not None else None  # Store in the dictionary

            # Add the run_name as a column to the parameter dictionary
            run_values['CropParameterItem'] = run_name

            param_list.append(run_values)  # Append the parameter dictionary to the list

        # Convert the list of dictionaries into a DataFrame
        param_df = pd.DataFrame(param_list)

        return param_df# Return the constructed dictionary

    def execute(self):
        """Run the project logic."""
        print("Executing run with the following inputs:")
        self.display_inputs()


    def display_inputs(self):
        """Display parsed inputs."""
        print(self.parameters)