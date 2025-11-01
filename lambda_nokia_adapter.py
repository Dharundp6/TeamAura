import json
import time

def lambda_handler(event, context):
    """
    Nokia RAN Adapter
    Simulates Nokia proprietary API calls for RAN management
    """
    
    print(f"Nokia Adapter invoked with event: {json.dumps(event)}")
    
    tool = event.get('tool')
    target = event.get('target')
    
    # Simulate Nokia API processing time
    time.sleep(0.2)
    
    response_data = {}
    
    if tool == 'get_kpis':
        print(f"Nokia API: Getting KPIs for {target}")
        
        if 'DUB-07' in target:
            response_data = {
                'vendor': 'Nokia',
                'api_version': '5G-SA-R16',
                'cell_id': target,
                'status': 'HEALTHY',
                'radio_signal_dbm': -75,
                'packet_loss_percent': 0.1,
                'throughput_mbps': 850,
                'connected_users': 245,
                'timestamp': int(time.time())
            }
        else:
            response_data = {
                'vendor': 'Nokia',
                'error': 'Cell ID not found in Nokia network'
            }
    
    elif tool == 'measure_latency':
        print(f"Nokia Transport API: Measuring latency for {target}")
        
        if 'DUB-07-FIBER' in target:
            response_data = {
                'vendor': 'Nokia',
                'link_id': target,
                'status': 'DEGRADED',
                'latency_ms': 500,
                'packet_loss_percent': 45.0,
                'jitter_ms': 150,
                'link_type': 'fiber',
                'timestamp': int(time.time())
            }
        elif 'DUB-07-NTN' in target:
            response_data = {
                'vendor': 'Nokia',
                'link_id': target,
                'status': 'HEALTHY',
                'latency_ms': 120,
                'packet_loss_percent': 0.5,
                'jitter_ms': 5,
                'link_type': 'satellite',
                'timestamp': int(time.time())
            }
        else:
            response_data = {
                'vendor': 'Nokia',
                'link_id': target,
                'status': 'HEALTHY',
                'latency_ms': 10,
                'packet_loss_percent': 0.0
            }
    
    elif tool == 'initiate_failover':
        print(f"Nokia Orchestration API: Initiating failover for {target}")
        
        response_data = {
            'vendor': 'Nokia',
            'operation': 'NTN_FAILOVER',
            'site_id': target,
            'status': 'SUCCESS',
            'previous_link': f'{target}-FIBER',
            'new_active_link': f'{target}-NTN',
            'failover_time_ms': 1250,
            'affected_users': 245,
            'timestamp': int(time.time())
        }
    
    else:
        return {
            'statusCode': 400,
            'body': json.dumps({
                'error': f'Unknown tool: {tool}',
                'vendor': 'Nokia'
            })
        }
    
    return {
        'statusCode': 200,
        'body': json.dumps(response_data)
    }