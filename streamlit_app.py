import streamlit as st
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd

# Function to parse the XML file and extract nodes, edges, and flows
def parse_xml(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    
    nodes = {}
    flows = defaultdict(list)
    
    for obj in root.findall('.//object'):
        obj_id = obj.get('id')
        label = obj.get('label')
        response_time = obj.get('responseTime') or obj.get('RenderingTime')
        app_type = None

        # Find the appType attribute from the child mxCell element's style attribute
        for cell in obj.findall('mxCell'):
            style = cell.get('style')
            if style:
                for style_param in style.split(';'):
                    if 'appType' in style_param:
                        app_type = style_param.split('=')[1]
                        break
        
        # Only add nodes with responseTime
        if response_time:
            nodes[obj_id] = {
                'id': obj_id,
                'label': label,
                'response_time': float(response_time),
                'app_type': app_type
            }

    # Then, parse flows and link source and target nodes
    for obj in root.findall('.//object'):
        obj_id = obj.get('id')
        label = obj.get('label')
        flow = obj.get('flow')
        step = obj.get('step')
        
        # Find source and target from the mxCell
        for cell in obj.findall('mxCell'):
            source = cell.get('source')
            target = cell.get('target')
        
        # Only consider objects with flow and step attributes
        if flow and step:
            flows[flow].append({
                'id': obj_id,
                'label': label,
                'response_time': float(response_time) if response_time else 0,
                'step': int(step),
                'app_type': 'flow',
                #'source': nodes[source],
                #'target': nodes[target],
                'source_label': nodes[source]['label'] if source in nodes else '',
                'target_label': nodes[target]['label'] if target in nodes else '',
                'target_response_time': nodes[target]['response_time'] if target in nodes else 0
            })
    
    return nodes, flows

# Function to calculate the total response time for each flow
def calculate_flow_response_times(flows):
    flow_response_times = []
    for flow_id, steps in flows.items():
        steps_sorted = sorted(steps, key=lambda x: x['step'])
        total_response_time = sum(step['target_response_time'] for step in steps_sorted)

        first_step = steps_sorted[0]
        last_step = steps_sorted[-1]
        
        flow_response_times.append({
            'Flow ID': flow_id,
            #'Flow Name': step['label'],
            'Source': first_step['source_label'],
            'Target': last_step['target_label'],
            'Total Response Time (ms)': total_response_time
        })
    return flow_response_times


st.title("Architecture flows report")
uploaded_file = st.file_uploader("Upload Draw.io XML file")

if uploaded_file is not None:
    xml_content = uploaded_file.read().decode("utf-8")
    nodes, flows = parse_xml(xml_content)
    
    with st.expander("Xml to JSON"):
        # Display nodes and flows
        st.write("Nodes:", nodes)
        st.write("Flows:", flows)
    
    # Calculate response times for each flow
    flow_response_times = calculate_flow_response_times(flows)
    
    # Display the results in a table
    st.write("Flows list:")
    df = pd.DataFrame(flow_response_times)
    st.table(df)
    
    # Display the detailed flow information
    with st.expander('Detailed Flow Information:'):
        for flow_id, steps in flows.items():
            st.write(f"Flow ID: {flow_id}")
            flow_df = pd.DataFrame(steps)
            st.table(flow_df)