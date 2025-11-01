import boto3
import json

def check_bedrock_quotas():
    """Check current Bedrock service quotas"""
    
    service_quotas = boto3.client('service-quotas', region_name='us-east-1')
    bedrock = boto3.client('bedrock', region_name='us-east-1')
    
    print("=" * 70)
    print("AWS Bedrock Service Quotas")
    print("=" * 70)
    
    # List of quota codes to check
    quota_codes = [
        'L-E7E0F8D4',  # InvokeModel requests per minute
        'L-4B3D527C',  # InvokeModelWithResponseStream requests per minute
    ]
    
    for code in quota_codes:
        try:
            response = service_quotas.get_service_quota(
                ServiceCode='bedrock',
                QuotaCode=code
            )
            
            quota = response['Quota']
            print(f"\n📊 {quota['QuotaName']}")
            print(f"   Current Limit: {quota['Value']}")
            print(f"   Adjustable: {quota.get('Adjustable', 'Unknown')}")
            
        except Exception as e:
            print(f"Could not retrieve quota {code}: {e}")
    
    print("\n" + "=" * 70)
    print("\n💡 TIP: If you need higher limits, request a quota increase at:")
    print("   https://console.aws.amazon.com/servicequotas/")
    print("=" * 70)

if __name__ == "__main__":
    check_bedrock_quotas()