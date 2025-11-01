#!/bin/bash

echo "🔐 Creating IAM Role for Lambda functions..."

# Create trust policy
cat > trust-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "lambda.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF

# Create the role
aws iam create-role \
    --role-name AURA-Lambda-Execution-Role \
    --assume-role-policy-document file://trust-policy.json

# Attach basic Lambda execution policy
aws iam attach-role-policy \
    --role-name AURA-Lambda-Execution-Role \
    --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole

# Create policy for Lambda to invoke other Lambdas
cat > lambda-invoke-policy.json << EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "lambda:InvokeFunction"
      ],
      "Resource": "*"
    }
  ]
}
EOF

aws iam put-role-policy \
    --role-name AURA-Lambda-Execution-Role \
    --policy-name LambdaInvokePolicy \
    --policy-document file://lambda-invoke-policy.json

echo "✅ IAM Role created: AURA-Lambda-Execution-Role"

# Get the role ARN
ROLE_ARN=$(aws iam get-role --role-name AURA-Lambda-Execution-Role --query 'Role.Arn' --output text)
echo "📝 Role ARN: $ROLE_ARN"
echo ""
echo "⏳ Waiting 10 seconds for IAM role to propagate..."
sleep 10