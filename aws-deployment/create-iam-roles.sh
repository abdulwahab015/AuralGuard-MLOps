#!/bin/bash

# Create IAM roles required for ECS Fargate

set -e

ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🔐 Creating IAM roles for ECS Fargate..."
echo "Account ID: $ACCOUNT_ID"
echo ""

# Create execution role (required for CloudWatch logs)
echo "📝 Creating ecsTaskExecutionRole..."
if aws iam get-role --role-name ecsTaskExecutionRole 2>/dev/null; then
    echo "✅ Role already exists"
else
    aws iam create-role \
        --role-name ecsTaskExecutionRole \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' > /dev/null
    
    # Attach managed policy
    aws iam attach-role-policy \
        --role-name ecsTaskExecutionRole \
        --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy
    
    echo "✅ Execution role created"
fi

# Create task role (optional, but referenced in task definition)
echo ""
echo "📝 Creating ecsTaskRole..."
if aws iam get-role --role-name ecsTaskRole 2>/dev/null; then
    echo "✅ Role already exists"
else
    aws iam create-role \
        --role-name ecsTaskRole \
        --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [{
                "Effect": "Allow",
                "Principal": {"Service": "ecs-tasks.amazonaws.com"},
                "Action": "sts:AssumeRole"
            }]
        }' > /dev/null
    
    echo "✅ Task role created"
fi

echo ""
echo "✅ IAM roles created successfully!"
echo ""
echo "Now run: ./deploy-ecs.sh again"

