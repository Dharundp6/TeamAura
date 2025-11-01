import boto3
import json

def test_claude_models():
    bedrock_runtime = boto3.client(
        service_name='bedrock-runtime',
        region_name='us-east-1'
    )
    
    # Available Claude models from your account
    models_to_test = [
        ('us.anthropic.claude-sonnet-4-20250514-v1:0', 'Claude Sonnet 4'),
        ('us.anthropic.claude-3-7-sonnet-20250219-v1:0', 'Claude 3.7 Sonnet'),
        ('us.anthropic.claude-3-5-sonnet-20241022-v2:0', 'Claude 3.5 Sonnet v2'),
        ('us.anthropic.claude-3-5-haiku-20241022-v1:0', 'Claude 3.5 Haiku'),
    ]
    
    request_body = {
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": 200,
        "messages": [
            {
                "role": "user",
                "content": "Hello! Please introduce yourself briefly."
            }
        ]
    }
    
    print("Testing Available Claude Models")
    print("=" * 70)
    
    for model_id, model_name in models_to_test:
        print(f"\n🤖 Testing: {model_name}")
        print(f"   Model ID: {model_id}")
        print("-" * 70)
        
        try:
            response = bedrock_runtime.invoke_model(
                modelId=model_id,
                body=json.dumps(request_body)
            )
            
            response_body = json.loads(response['body'].read())
            message = response_body['content'][0]['text']
            usage = response_body.get('usage', {})
            
            print(f"✓ SUCCESS!")
            print(f"\nResponse: {message}")
            print(f"\n📊 Token Usage:")
            print(f"   Input: {usage.get('input_tokens')} tokens")
            print(f"   Output: {usage.get('output_tokens')} tokens")
            
            # Calculate approximate cost
            input_cost = usage.get('input_tokens', 0) * 0.003 / 1000
            output_cost = usage.get('output_tokens', 0) * 0.015 / 1000
            total_cost = input_cost + output_cost
            print(f"   Approximate cost: ${total_cost:.6f}")
            
        except Exception as e:
            print(f"✗ FAILED: {str(e)}")
        
        print("-" * 70)

if __name__ == "__main__":
    test_claude_models()