import os
import csv
import difflib
import json
from lxml import etree
from dotenv import dotenv_values
from configparser import ConfigParser, MissingSectionHeaderError
 
def parse_xml(file_path):
    try:
        if os.path.exists(file_path):
            tree = etree.parse(file_path)
            root = tree.getroot()
            # Basic example: Extracting tag names and their text content into a dictionary
            data = {child.tag: child.text for child in root}
            return data
        else:
            print(f"File not found: {file_path}")
            return None
    except etree.XMLSyntaxError as e:
        print(f"XML parsing error in file '{file_path}': {e}")
        return None
 
def parse_json(file_path):
    with open(file_path, 'r') as json_file:
        return json.load(json_file)
 
def parse_text(file_path):
    with open(file_path, 'r') as text_file:
        return text_file.read()
 
def parse_env(file_path):
    return dotenv_values(file_path)
 
def parse_properties(file_path):
    from configparser import ConfigParser, MissingSectionHeaderError
    config = ConfigParser()
 
    # Artificially add a default section header to file content
    with open(file_path, 'r') as f:
        file_content = "[DEFAULT]\n" + f.read()
 
    # Use StringIO to simulate reading from a file
    from io import StringIO
    config.read_file(StringIO(file_content))
 
    properties_dict = {section: dict(config.items(section)) for section in config.sections()}
    return properties_dict
 
def parse_file(file_path):
    _, file_extension = os.path.splitext(file_path)
    parse_functions = {
        '.xml': parse_xml,
        '.json': parse_json,
        '.txt': parse_text,
        '.env': parse_env,
        '.properties': parse_properties,
    }
    return parse_functions.get(file_extension, lambda x: None)(file_path)
 
def compare_files(file1, file2):
    data1 = parse_file(file1)
    data2 = parse_file(file2)
    if data1 == data2:
        return None, None  # No differences
 
    differences = list(difflib.unified_diff(
        str(data1).splitlines(),
        str(data2).splitlines(),
        fromfile=file1,
        tofile=file2,
        lineterm=''))
 
    # Filter differences for lines starting with '-' and '+'
    deletions = "\n".join([line for line in differences if line.startswith('-') and not line.startswith('---')])
    additions = "\n".join([line for line in differences if line.startswith('+') and not line.startswith('+++')])
    return deletions, additions
 
def compare_environment_directories(base_dir, env1, env2, csv_writer):
    env_path1 = os.path.join(base_dir, env1)
    env_path2 = os.path.join(base_dir, env2)
 
    for app_name in os.listdir(env_path1):
        app_path1 = os.path.join(env_path1, app_name)
        app_path2 = os.path.join(env_path2, app_name)
 
        if os.path.exists(app_path1) and os.path.exists(app_path2):
            for file_name in os.listdir(app_path1):
                file_path1 = os.path.join(app_path1, file_name)
                file_path2 = os.path.join(app_path2, file_name)
 
                if os.path.exists(file_path2):
                    deletions, additions = compare_files(file_path1, file_path2)
                    if deletions or additions:
                        csv_writer.writerow([app_name, file_name, deletions, additions])
 
def main():
    base_dir = "Directory to store csv file"
    environment_dirs = [dir for dir in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, dir))]
    with open('differences.csv', 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(["Application", "File", "env1 (Deletions)", "env2 (Additions)"])
 
        for i, env1 in enumerate(environment_dirs):
            for env2 in environment_dirs[i+1:]:
                compare_environment_directories(base_dir, env1, env2, csv_writer)
 
if __name__ == "__main__":
    main()
