import json
import time

def lambda_handler(event, context):
    """
    Ericsson RAN Adapter
    Simulates Ericsson proprietary API calls
    """
    
    print(f"Ericsson Adapter invoked with event: {json.dumps(event)}")
    
    tool = event.get('tool')
    target = event.get('target')
    
    time.sleep(0.2)
    
    response_data = {}
    
    if tool == 'get_kpis':
        print(f"Ericsson ENM API: Getting KPIs for {target}")
        
        if 'LON-15' in target:
            response_data = {
                'vendor': 'Ericsson',
                'api_version': 'ENM-22.1',
                'cell_id': target,
                'status': 'HEALTHY',
                'rsrp_dbm': -72,
                'sinr_db': 18,
                'packet_loss_percent': 0.05,
                'dl_throughput_mbps': 920,
                'ul_throughput_mbps': 380,
                'active_ues': 312,
                'timestamp': int(time.time())
            }
        else:
            response_data = {
                'vendor': 'Ericsson',
                'error': 'Cell ID not found in Ericsson network'
            }
    
    elif tool == 'measure_latency':
        print(f"Ericsson Transport API: Measuring latency for {target}")
        
        response_data = {
            'vendor': 'Ericsson',
            'link_id': target,
            'status': 'HEALTHY',
            'rtt_ms': 12,
            'packet_loss_percent': 0.02,
            'bandwidth_gbps': 10,
            'timestamp': int(time.time())
        }
    
    elif tool == 'initiate_failover':
        print(f"Ericsson Orchestration: Initiating failover for {target}")
        
        response_data = {
            'vendor': 'Ericsson',
            'operation': 'LINK_FAILOVER',
            'site_id': target,
            'status': 'SUCCESS',
            'new_active_link': f'{target}-BACKUP',
            'timestamp': int(time.time())
        }
    
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Unknown tool: {tool}',
                'vendor': 'Ericsson'
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }