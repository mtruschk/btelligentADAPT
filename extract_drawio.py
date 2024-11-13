import xml.etree.ElementTree as ET
import argparse
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
    
def to_markdown_file(xml_path, shapes, connections):
    # Generate markdown filename
    base_name = os.path.splitext(xml_path)[0]
    md_filename = f"{base_name}.md"

    with open(md_filename, 'w') as md_file:
        # Write shapes to markdown
        md_file.write(f"# Übersicht zum Diagramm **{base_name}**:\n")
        md_file.write(f"## Shapes with Tooltip beginning 'ADAPT'\n")
        for shape in shapes:
            md_file.write(f"- **ID:** {shape['ID']}, **Label:** {shape['Label']}, **ADAPT Type:** {shape['ADAPT Type']}\n")
        
        # Write connections to markdown
        md_file.write("\n## Connections with Tooltip beginning 'ADAPT'\n")
        for connection in connections:
            md_file.write(f"- **ID:** {connection['ID']}, **Label:** {connection['Label']}, **Source:** {connection['Source']}, **Target:** {connection['Target']}, **ADAPT Type:** {connection['ADAPT Type']}, **Start Arrow:** {connection['Start Arrow']}, **End Arrow:** {connection['End Arrow']}\n")
            
            md_file.write(f"- **ID:** {connection['ID']}, **Label:** {connection['Label']}, **Source:** {connection['Source']}, **Target:** {connection['Target']}, **ADAPT Type:** {connection['ADAPT Type']}, **Start Arrow:** {connection['Start Arrow']}, **End Arrow:** {connection['End Arrow']}\n")
            md_file.write(f"\n\n### und hier haben wir auch das Diagramm dazu:\n")
        
        md_file.write(f"![Diagramm {base_name}]({base_name}.png)\n")

    print(f"Markdown file '{md_filename}' has been created.")

def main():
    parser = argparse.ArgumentParser(description='Extract draw.io shape and connection information from XML.')
    parser.add_argument('xml_path', help='Path to the draw.io XML file')
    args = parser.parse_args()
    xml_path = args.xml_path

    shapes, connections = extract_information(xml_path)
    
    # Print extracted shapes
    print("Shapes (Nodes):")
    for shape in shapes:
        print(f"ID: {shape['ID']}, Label: {shape['Label']}, ADAPT Type: {shape['ADAPT Type']}")

    # Print extracted connections
    print("\nConnections (Edges):")
    for connection in connections:
        print(f"ID: {connection['ID']}, Label: {connection['Label']}, Source: {connection['Source']}, Target: {connection['Target']}, ADAPT Type: {connection['ADAPT Type']}, Start Arrow: {connection['Start Arrow']}, End Arrow: {connection['End Arrow']}")
        
    # Print extracted information
    to_markdown_file(xml_path, shapes, connections)

if __name__ == "__main__":
    main()
