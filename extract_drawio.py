import xml.etree.ElementTree as ET
import argparse
import subprocess
import yaml
import os

def extract_information(xml_path):
    try:
        # Parse the XML file
        tree = ET.parse(xml_path)
        root = tree.getroot()
   
    except (ET.ParseError, FileNotFoundError) as e:
        print(f"Error reading the XML file: {e}")
        return [], []

    # Namespace handling if necessary
    #namespace = {'': 'http://www.w3.org/1999/xhtml'}

    # Lists to store data
    shapes = []
    connections = []

    # Iterate through UserObjects and mxCells
    for user_object in root.findall('.//UserObject') + root.findall('.//object'):
        adapttype = user_object.get('btelligentADAPTType')
        label = user_object.get('label')
        shape_id = user_object.get('id')

        # Determine if this is a shape or a connection
        if adapttype and adapttype in ["Dimension", "LoosePrecedence", "StrictPrecedence", "Hierarchy", "DimensionMember", "DimensionScope", "Function", "HierarchyLevel", "Attribute", "MeasureGroup", "MeasureDimension"]:
            mx_cell = user_object.find('./mxCell')
            
            if mx_cell.get('edge') == '1':  # It's a connection
                source = mx_cell.get('source')
                target = mx_cell.get('target')
                style = mx_cell.get('style')
                start_arrow = extract_style_value(style, 'startArrow')
                end_arrow = extract_style_value(style, 'endArrow')
                
                connection_info = {
                    'ID': shape_id,
                    'Label': label,
                    'Source': source,
                    'Target': target,
                    'ADAPT Type': adapttype,
                    'Start Arrow': start_arrow,
                    'End Arrow': end_arrow
                }
                connections.append(connection_info)
            else:  # It's a shape
                shape_info = {
                    'ID': shape_id,
                    'Label': label,
                    'ADAPT Type': adapttype
                }
                shapes.append(shape_info)
    
    return shapes, connections

def extract_style_value(style, key):
    # Helper function to extract values from the style attribute
    style_dict = dict(item.split('=') for item in style.split(';') if '=' in item)
    return style_dict.get(key, 'None')

def load_config(yaml_path):

    with open(yaml_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def export_drawio_to_png(drawio_executable, input_file, output_file):
    # Stellen Sie sicher, dass das Verzeichnis für die Ausgabe existiert
    output_dir = os.path.dirname(output_file)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Konstruktion des Befehls
    command = [
        drawio_executable, 
        "--export", 
        "--format", "png", 
        "--output", output_file, 
        input_file
    ]

    # Ausführung des Befehls
    try:
        subprocess.run(command, check=True)
        print(f"Export erfolgreich: {output_file}")
    except subprocess.CalledProcessError as e:
        print(f"Fehler beim Exportieren: {e}")

    
def to_markdown_file(xml_path, shapes, connections):
    # Generate markdown filename
    base_name = os.path.splitext(xml_path)[0]
    md_filename = f"{base_name}.md"
    diagram_name = os.path.splitext(os.path.basename(xml_path))[0]

    with open(md_filename, 'w') as md_file:
        # Write shapes to markdown
        md_file.write(f"# Übersicht zum Diagramm **{diagram_name}**:\n")
        md_file.write(f"## Shapes with Tooltip beginning 'ADAPT'\n")
        for shape in shapes:
            md_file.write(f"- **ID:** {shape['ID']}, **Label:** {shape['Label']}, **ADAPT Type:** {shape['ADAPT Type']}\n")
        
        # Write connections to markdown
        md_file.write("\n## Connections with Tooltip beginning 'ADAPT'\n")
        for connection in connections:
            md_file.write(f"- **ID:** {connection['ID']}, **Label:** {connection['Label']}, **Source:** {connection['Source']}, **Target:** {connection['Target']}, **ADAPT Type:** {connection['ADAPT Type']}, **Start Arrow:** {connection['Start Arrow']}, **End Arrow:** {connection['End Arrow']}\n")
                                    
        md_file.write(f"\n\n### und hier haben wir auch das Diagramm dazu:\n")
        md_file.write(f"![Diagramm {diagram_name}](../png{diagram_name}.png)\n")

    print(f"Markdown file '{md_filename}' has been created.")

def main():
    # Set the directory path to the "drawio" folder in the current working directory
    drawio_directory = os.path.join(os.getcwd(), 'drawio')
    docs_directory = os.path.join(os.getcwd(), 'docs')
    png_directory = os.path.join(os.getcwd(), 'png')
    
    # Laden der Konfiguration aus der YAML-Datei
    config = load_config('config.yaml')
    drawio_executable = config.get('drawio_executable_path')

    if not drawio_executable:
        print("Draw.io executable path is not set in the configuration file.")
        return

    # Check if the directory exists
    if not os.path.exists(png_directory):
        print(f"The directory '{png_directory}' does not exist.")
        return

    # Check if the directory exists
    if not os.path.exists(drawio_directory):
        print(f"The directory '{drawio_directory}' does not exist.")
        return

    # Check if the directory exists
    if not os.path.exists(docs_directory):
        print(f"The directory '{docs_directory}' does not exist.")
        return

    for root_dir, dirs, files in os.walk(drawio_directory):

            for file in files:

                if file.endswith('.drawio'):

                    drawio_path = os.path.join(drawio_directory, file)
                    docs_path = os.path.join(docs_directory, file)
                    
                    base_name = os.path.splitext(os.path.join(png_directory, file))[0]
                    png_path = f"{base_name}.png"

                    print(f"Processing file: {drawio_path}")
                    print(f"PNG file: {png_path}")
                    
                    export_drawio_to_png(drawio_executable, drawio_path, png_path)

                    shapes, connections = extract_information(drawio_path)
                    
                    # Print extracted shapes
                    print("Shapes (Nodes):")
                    for shape in shapes:
                        print(f"ID: {shape['ID']}, Label: {shape['Label']}, ADAPT Type: {shape['ADAPT Type']}")

                    # Print extracted connections
                    print("\nConnections (Edges):")
                    for connection in connections:
                        print(f"ID: {connection['ID']}, Label: {connection['Label']}, Source: {connection['Source']}, Target: {connection['Target']}, ADAPT Type: {connection['ADAPT Type']}, Start Arrow: {connection['Start Arrow']}, End Arrow: {connection['End Arrow']}")
                        
                    # Print extracted information
                    to_markdown_file(docs_path, shapes, connections)

if __name__ == "__main__":
    main()
