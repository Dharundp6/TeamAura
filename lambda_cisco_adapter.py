import json
import time

def lambda_handler(event, context):
    """
    Cisco Transport Adapter
    Simulates Cisco transport network API calls
    """
    
    print(f"Cisco Adapter invoked with event: {json.dumps(event)}")
    
    tool = event.get('tool')
    target = event.get('target')
    
    time.sleep(0.2)
    
    response_data = {}
    
    if tool == 'get_kpis':
        print(f"Cisco DNA Center API: Getting device KPIs for {target}")
        
        if 'PAR-03' in target:
            response_data = {
                'vendor': 'Cisco',
                'api_version': 'DNA-Center-2.3',
                'device_id': target,
                'status': 'REACHABLE',
                'cpu_percent': 45,
                'memory_percent': 62,
                'uptime_hours': 720,
                'timestamp': int(time.time())
            }
        else:
            response_data = {
                'vendor': 'Cisco',
                'error': 'Device not found in Cisco network'
            }
    
    elif tool == 'measure_latency':
        print(f"Cisco SD-WAN API: Measuring path latency for {target}")
        
        response_data = {
            'vendor': 'Cisco',
            'path_id': target,
            'status': 'UP',
            'latency_ms': 8,
            'loss_percent': 0.01,
            'jitter_ms': 2,
            'available_bandwidth_mbps': 9500,
            'timestamp': int(time.time())
        }
    
    elif tool == 'initiate_failover':
        print(f"Cisco SD-WAN Orchestration: Initiating path failover for {target}")
        
        response_data = {
            'vendor': 'Cisco',
            'operation': 'PATH_PREFERENCE_CHANGE',
            'site_id': target,
            'status': 'SUCCESS',
            'new_primary_path': f'{target}-MPLS-BACKUP',
            'convergence_time_ms': 800,
            'timestamp': int(time.time())
        }
    
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Unknown tool: {tool}',
                'vendor': 'Cisco'
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }