import streamlit as st
import xml.etree.ElementTree as ET
from collections import defaultdict
import pandas as pd

# Function to parse the XML file and extract nodes and edges
def parse_xml(xml_content):
    tree = ET.ElementTree(ET.fromstring(xml_content))
    root = tree.getroot()
    
    nodes = {}
    edges = []
    flows = defaultdict(list)
    
    for cell in root.findall('.//mxCell'):
        cell_id = cell.get('id')
        if cell.get('source') and cell.get('target'):
            # It's an edge
            edges.append({
                'source': cell.get('source'),
                'target': cell.get('target')
            })
        else:
            # It's a node
            data = {elem.get('key'): elem.text for elem in cell.findall('data')}
            flow = data.get('flow')
            step = data.get('step')
            if flow and step:
                flows[flow].append({
                    'id': cell_id,
                    'response_time': float(data.get('responseTime', 0)),
                    'step': int(step)
                })
            else:
                nodes[cell_id] = {
                    'id': cell_id,
                    'response_time': float(data.get('responseTime', 0)),
                    'flow': flow,
                    'step': step
                }
    
    return nodes, edges, flows

# Function to calculate the total response time for each flow
def calculate_flow_response_times(flows):
    flow_response_times = {}
    for flow_id, steps in flows.items():
        steps_sorted = sorted(steps, key=lambda x: x['step'])
        total_response_time = sum(step['response_time'] for step in steps_sorted)
        flow_response_times[flow_id] = total_response_time
    return flow_response_times


st.title("Architecture Metrics Calculator")
uploaded_file = st.file_uploader("Upload Draw.io XML file")

if uploaded_file is not None:
    xml_content = uploaded_file.read().decode("utf-8")
    nodes, edges, flows = parse_xml(xml_content)
    
    # Display nodes, edges, and flows
    st.write("Nodes:", nodes)
    st.write("Edges:", edges)
    st.write("Flows:", flows)
    
    # Calculate response times for each flow
    flow_response_times = calculate_flow_response_times(flows)
    
    # Display the results in a table
    st.write("Flow Response Times:")
    df = pd.DataFrame(list(flow_response_times.items()), columns=["Flow ID", "Total Response Time (ms)"])
    st.table(df)