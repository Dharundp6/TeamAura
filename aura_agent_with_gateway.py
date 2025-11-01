import boto3
import json
import requests
from typing import List, Dict
import time

# Load gateway configuration
with open('gateway_config.json', 'r') as f:
    GATEWAY_CONFIG = json.load(f)

GATEWAY_ENDPOINT = GATEWAY_CONFIG['endpoint']

# Rest of your AURAAgent code...
# But modify the tool functions to call the API Gateway

def get_cell_kpis(cell_id: str) -> dict:
    """Call API Gateway instead of mocked data"""
    print(f"🔍 Checking KPIs for {cell_id} via MCP Gateway...")
    
    response = requests.post(
        GATEWAY_ENDPOINT,
        json={
            "tool": "get_cell_kpis",
            "target": cell_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {})
    else:
        return {"error": "Gateway request failed"}

def measure_link_latency(link_id: str) -> dict:
    """Call API Gateway instead of mocked data"""
    print(f"📡 Measuring latency for {link_id} via MCP Gateway...")
    
    response = requests.post(
        GATEWAY_ENDPOINT,
        json={
            "tool": "measure_link_latency",
            "target": link_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {})
    else:
        return {"error": "Gateway request failed"}

def initiate_ntn_failover(site_id: str) -> dict:
    """Call API Gateway instead of mocked data"""
    print(f"⚠️  Executing NTN failover for {site_id} via MCP Gateway...")
    
    response = requests.post(
        GATEWAY_ENDPOINT,
        json={
            "tool": "initiate_ntn_failover",
            "target": site_id
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        return data.get('data', {})
    else:
        return {"error": "Gateway request failed"}

# Import the rest of your AURAAgent class from aura_interactive.py
# ... (keep all the AURAAgent class code)