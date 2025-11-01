import requests
import json

def test_gateway():
    """Test the AURA MCP Gateway"""
    
    # Load configuration
    with open('gateway_config.json', 'r') as f:
        config = json.load(f)
    
    endpoint = config['endpoint']
    
    print("=" * 70)
    print("AURA MCP Gateway - Testing")
    print("=" * 70)
    print(f"Endpoint: {endpoint}\n")
    
    # Test cases
    test_cases = [
        {
            "name": "Nokia - Get Cell KPIs",
            "payload": {
                "tool": "get_cell_kpis",
                "target": "DUB-07"
            }
        },
        {
            "name": "Nokia - Measure Fiber Latency",
            "payload": {
                "tool": "measure_link_latency",
                "target": "DUB-07-FIBER"
            }
        },
        {
            "name": "Nokia - Measure NTN Latency",
            "payload": {
                "tool": "measure_link_latency",
                "target": "DUB-07-NTN"
            }
        },
        {
            "name": "Ericsson - Get Cell KPIs",
            "payload": {
                "tool": "get_cell_kpis",
                "target": "LON-15"
            }
        },
        {
            "name": "Cisco - Get Device KPIs",
            "payload": {
                "tool": "get_cell_kpis",
                "target": "PAR-03"
            }
        },
        {
            "name": "Nokia - Initiate Failover",
            "payload": {
                "tool": "initiate_ntn_failover",
                "target": "DUB-07"
            }
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['name']}")
        print("-" * 70)
        
        try:
            response = requests.post(
                endpoint,
                json=test['payload'],
                headers={'Content-Type': 'application/json'},
                timeout=10
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success!")
                print(f"Vendor: {data.get('vendor')}")
                print(f"Response Data:")
                print(json.dumps(data.get('data'), indent=2))
            else:
                print(f"❌ Error: {response.text}")
                
        except Exception as e:
            print(f"❌ Exception: {str(e)}")
    
    print("\n" + "=" * 70)
    print("Testing Complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_gateway()