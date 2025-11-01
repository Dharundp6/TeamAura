import boto3
import json

def list_inference_profiles():
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    
    try:
        response = bedrock.list_inference_profiles()
        
        print("Available Inference Profiles:")
        print("=" * 70)
        
        for profile in response.get('inferenceProfileSummaries', []):
            print(f"\nProfile ID: {profile['inferenceProfileId']}")
            print(f"Name: {profile['inferenceProfileName']}")
            print(f"Type: {profile['type']}")
            if 'models' in profile:
                print(f"Models: {profile['models']}")
            print("-" * 70)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    list_inference_profiles()