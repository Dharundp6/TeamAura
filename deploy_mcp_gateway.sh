#!/bin/bash

set -e  # Exit on error

echo "🚀 Deploying AURA MCP Gateway Infrastructure"
echo "============================================"
echo ""

# Get AWS Account ID
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"

echo "📋 AWS Account ID: $ACCOUNT_ID"
echo "📍 Region: $REGION"
echo ""

# Get IAM Role ARN
ROLE_ARN="arn:aws:iam::${ACCOUNT_ID}:role/AURA-Lambda-Execution-Role"
echo "🔐 Using IAM Role: $ROLE_ARN"
echo ""

# Function to create or update Lambda
deploy_lambda() {
    local FUNCTION_NAME=$1
    local HANDLER=$2
    local ZIP_FILE=$3
    local DESCRIPTION=$4
    
    echo "📦 Deploying Lambda: $FUNCTION_NAME"
    
    # Check if function exists
    if aws lambda get-function --function-name $FUNCTION_NAME 2>/dev/null; then
        echo "   ↻ Updating existing function..."
        aws lambda update-function-code \
            --function-name $FUNCTION_NAME \
            --zip-file fileb://$ZIP_FILE \
            --region $REGION > /dev/null
        
        aws lambda update-function-configuration \
            --function-name $FUNCTION_NAME \
            --handler $HANDLER \
            --timeout 30 \
            --memory-size 256 \
            --region $REGION > /dev/null
    else
        echo "   ✨ Creating new function..."
        aws lambda create-function \
            --function-name $FUNCTION_NAME \
            --runtime python3.11 \
            --role $ROLE_ARN \
            --handler $HANDLER \
            --timeout 30 \
            --memory-size 256 \
            --description "$DESCRIPTION" \
            --zip-file fileb://$ZIP_FILE \
            --region $REGION > /dev/null
    fi
    
    echo "   ✅ $FUNCTION_NAME deployed"
}

# Package and deploy Nokia Adapter
echo "1️⃣  Nokia Adapter"
zip -q nokia_adapter.zip lambda_nokia_adapter.py
deploy_lambda \
    "AURA-Nokia-Adapter" \
    "lambda_nokia_adapter.lambda_handler" \
    "nokia_adapter.zip" \
    "AURA Nokia RAN Adapter for vendor-specific API calls"

# Package and deploy Ericsson Adapter
echo ""
echo "2️⃣  Ericsson Adapter"
zip -q ericsson_adapter.zip lambda_ericsson_adapter.py
deploy_lambda \
    "AURA-Ericsson-Adapter" \
    "lambda_ericsson_adapter.lambda_handler" \
    "ericsson_adapter.zip" \
    "AURA Ericsson RAN Adapter for vendor-specific API calls"

# Package and deploy Cisco Adapter
echo ""
echo "3️⃣  Cisco Adapter"
zip -q cisco_adapter.zip lambda_cisco_adapter.py
deploy_lambda \
    "AURA-Cisco-Adapter" \
    "lambda_cisco_adapter.lambda_handler" \
    "cisco_adapter.zip" \
    "AURA Cisco Transport Adapter for vendor-specific API calls"

# Package and deploy Gateway Router
echo ""
echo "4️⃣  Gateway Router"
zip -q gateway_router.zip lambda_gateway_router.py
deploy_lambda \
    "AURA-Gateway-Router" \
    "lambda_gateway_router.lambda_handler" \
    "gateway_router.zip" \
    "AURA MCP Gateway Router - Routes requests to vendor adapters"

echo ""
echo "============================================"
echo "✅ All Lambda functions deployed successfully!"
echo ""
echo "📝 Deployed Functions:"
echo "   - AURA-Nokia-Adapter"
echo "   - AURA-Ericsson-Adapter"
echo "   - AURA-Cisco-Adapter"
echo "   - AURA-Gateway-Router"
echo ""
echo "🌐 Next: Creating API Gateway..."