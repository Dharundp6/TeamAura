#!/bin/bash

set -e

echo "🌐 Creating AURA MCP API Gateway"
echo "================================"
echo ""

REGION="us-east-1"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

# Create REST API
echo "1️⃣  Creating REST API..."
API_ID=$(aws apigateway create-rest-api \
    --name "AURA-MCP-Gateway-API" \
    --description "API Gateway for AURA Multi-Vendor Network Operations" \
    --endpoint-configuration types=REGIONAL \
    --region $REGION \
    --query 'id' \
    --output text)

echo "   ✅ API Created: $API_ID"

# Get root resource ID
ROOT_ID=$(aws apigateway get-resources \
    --rest-api-id $API_ID \
    --region $REGION \
    --query 'items[0].id' \
    --output text)

# Create /tools resource
echo ""
echo "2️⃣  Creating /tools resource..."
TOOLS_RESOURCE_ID=$(aws apigateway create-resource \
    --rest-api-id $API_ID \
    --parent-id $ROOT_ID \
    --path-part "tools" \
    --region $REGION \
    --query 'id' \
    --output text)

echo "   ✅ Resource created: /tools"

# Create POST method
echo ""
echo "3️⃣  Creating POST method..."
aws apigateway put-method \
    --rest-api-id $API_ID \
    --resource-id $TOOLS_RESOURCE_ID \
    --http-method POST \
    --authorization-type NONE \
    --region $REGION > /dev/null

echo "   ✅ POST method created"

# Set up Lambda integration
echo ""
echo "4️⃣  Setting up Lambda integration..."
LAMBDA_ARN="arn:aws:lambda:${REGION}:${ACCOUNT_ID}:function:AURA-Gateway-Router"

aws apigateway put-integration \
    --rest-api-id $API_ID \
    --resource-id $TOOLS_RESOURCE_ID \
    --http-method POST \
    --type AWS_PROXY \
    --integration-http-method POST \
    --uri "arn:aws:apigateway:${REGION}:lambda:path/2015-03-31/functions/${LAMBDA_ARN}/invocations" \
    --region $REGION > /dev/null

echo "   ✅ Lambda integration configured"

# Grant API Gateway permission to invoke Lambda
echo ""
echo "5️⃣  Granting API Gateway permissions..."
aws lambda add-permission \
    --function-name AURA-Gateway-Router \
    --statement-id apigateway-invoke-${API_ID} \
    --action lambda:InvokeFunction \
    --principal apigateway.amazonaws.com \
    --source-arn "arn:aws:execute-api:${REGION}:${ACCOUNT_ID}:${API_ID}/*" \
    --region $REGION 2>/dev/null || echo "   (Permission already exists)"

echo "   ✅ Permissions granted"

# Deploy API
echo ""
echo "6️⃣  Deploying API to 'prod' stage..."
aws apigateway create-deployment \
    --rest-api-id $API_ID \
    --stage-name prod \
    --stage-description "Production stage for AURA MCP Gateway" \
    --description "Initial deployment" \
    --region $REGION > /dev/null

echo "   ✅ API deployed"

# Save API endpoint
API_ENDPOINT="https://${API_ID}.execute-api.${REGION}.amazonaws.com/prod/tools"

echo ""
echo "================================"
echo "✅ API Gateway Setup Complete!"
echo ""
echo "📝 API Details:"
echo "   API ID: $API_ID"
echo "   Region: $REGION"
echo "   Endpoint: $API_ENDPOINT"
echo ""
echo "💾 Saving configuration..."

# Save to config file
cat > gateway_config.json << EOF
{
  "api_id": "$API_ID",
  "region": "$REGION",
  "endpoint": "$API_ENDPOINT",
  "deployed_at": "$(date -u +%Y-%m-%dT%H:%M:%SZ)"
}
EOF

echo "   ✅ Configuration saved to gateway_config.json"
echo ""
echo "🧪 Test with:"
echo "   curl -X POST $API_ENDPOINT \\"
echo "     -H 'Content-Type: application/json' \\"
echo "     -d '{\"tool\": \"get_cell_kpis\", \"target\": \"DUB-07\"}'"