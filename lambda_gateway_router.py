import json
import boto3
import os

lambda_client = boto3.client('lambda')

# Vendor mapping database
# In production, this would be DynamoDB or a configuration service
SITE_VENDOR_MAP = {
    'DUB-07': 'Nokia',
    'LON-15': 'Ericsson',
    'PAR-03': 'Cisco'
}

VENDOR_LAMBDA_MAP = {
    'Nokia': 'AURA-Nokia-Adapter',
    'Ericsson': 'AURA-Ericsson-Adapter',
    'Cisco': 'AURA-Cisco-Adapter'
}

TOOL_MAPPING = {
    'get_cell_kpis': 'get_kpis',
    'measure_link_latency': 'measure_latency',
    'initiate_ntn_failover': 'initiate_failover'
}

def extract_site_id(target: str) -> str:
    """Extract site ID from target string"""
    # Examples: "DUB-07", "DUB-07-FIBER", "LON-15-NTN"
    parts = target.split('-')
    if len(parts) >= 2:
        return f"{parts[0]}-{parts[1]}"
    return target

def lambda_handler(event, context):
    """
    AURA MCP Gateway Router
    Routes standardized tool requests to vendor-specific adapters
    """
    
    print(f"Gateway Router received event: {json.dumps(event)}")
    
    try:
        # Parse request body
        if isinstance(event.get('body'), str):
            body = json.loads(event['body'])
        else:
            body = event.get('body', event)
        
        tool = body.get('tool')
        target = body.get('target')
        params = body.get('params', {})
        
        if not tool or not target:
            return {
                'statusCode': 400,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': 'Missing required fields: tool and target'
                })
            }
        
        # Determine vendor from target site
        site_id = extract_site_id(target)
        vendor = SITE_VENDOR_MAP.get(site_id)
        
        if not vendor:
            return {
                'statusCode': 404,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': f'Unknown site: {site_id}',
                    'available_sites': list(SITE_VENDOR_MAP.keys())
                })
            }
        
        # Get the Lambda function for this vendor
        adapter_function = VENDOR_LAMBDA_MAP.get(vendor)
        
        if not adapter_function:
            return {
                'statusCode': 500,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    'error': f'No adapter configured for vendor: {vendor}'
                })
            }
        
        # Map tool name to vendor-specific tool name
        vendor_tool = TOOL_MAPPING.get(tool, tool)
        
        # Prepare payload for vendor adapter
        adapter_payload = {
            'tool': vendor_tool,
            'target': target,
            'params': params
        }
        
        print(f"Routing to {vendor} adapter: {adapter_function}")
        print(f"Adapter payload: {json.dumps(adapter_payload)}")
        
        # Invoke the vendor-specific adapter
        response = lambda_client.invoke(
            FunctionName=adapter_function,
            InvocationType='RequestResponse',
            Payload=json.dumps(adapter_payload)
        )
        
        # Parse adapter response
        response_payload = json.loads(response['Payload'].read())
        
        print(f"Adapter response: {json.dumps(response_payload)}")
        
        # Check if adapter returned an error
        if response_payload.get('statusCode') != 200:
            return {
                'statusCode': response_payload.get('statusCode', 500),
                'headers': {'Content-Type': 'application/json'},
                'body': response_payload.get('body', json.dumps({'error': 'Adapter error'}))
            }
        
        # Parse the adapter's body
        adapter_body = json.loads(response_payload['body'])
        
        # Return successful response with vendor info
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'X-AURA-Vendor': vendor,
                'X-AURA-Adapter': adapter_function
            },
            'body': json.dumps({
                'success': True,
                'vendor': vendor,
                'site_id': site_id,
                'tool': tool,
                'data': adapter_body
            })
        }
        
    except Exception as e:
        print(f"Error in gateway router: {str(e)}")
        import traceback
        traceback.print_exc()
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'error': 'Internal gateway error',
                'message': str(e)
            })
        }