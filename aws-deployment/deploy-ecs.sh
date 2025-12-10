#!/bin/bash

# AWS ECS Deployment Script for AuralGuard
# This script automates the ECS deployment process

set -e

# Configuration
REGION="us-east-1"
CLUSTER_NAME="auralguard-cluster"
SERVICE_NAME="auralguard-service"
TASK_DEFINITION="auralguard-mlops"
ECR_REPO="auralguard-mlops"
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)

echo "🚀 Starting AuralGuard ECS Deployment..."
echo "Region: $REGION"
echo "Account ID: $ACCOUNT_ID"
echo ""

# Step 1: Create ECR repository if it doesn't exist
echo "📦 Step 1: Setting up ECR repository..."
if ! aws ecr describe-repositories --repository-names $ECR_REPO --region $REGION 2>/dev/null; then
    echo "Creating ECR repository..."
    aws ecr create-repository --repository-name $ECR_REPO --region $REGION
    echo "✅ ECR repository created"
else
    echo "✅ ECR repository already exists"
fi

# Step 2: Build and push Docker image
echo ""
echo "🐳 Step 2: Building and pushing Docker image..."
ECR_URI="$ACCOUNT_ID.dkr.ecr.$REGION.amazonaws.com/$ECR_REPO"

# Login to ECR
aws ecr get-login-password --region $REGION | docker login --username AWS --password-stdin $ECR_URI

# Build image
echo "Building Docker image..."
cd "$(dirname "$0")/.."  # Go to project root
docker build -t $ECR_REPO:latest .

# Tag image
docker tag $ECR_REPO:latest $ECR_URI:latest

# Push image
echo "Pushing image to ECR..."
docker push $ECR_URI:latest
echo "✅ Image pushed to ECR"

# Step 3: Create CloudWatch log group
echo ""
echo "📊 Step 3: Setting up CloudWatch logs..."
if ! aws logs describe-log-groups --log-group-name-prefix "/ecs/$TASK_DEFINITION" --region $REGION 2>/dev/null | grep -q "/ecs/$TASK_DEFINITION"; then
    aws logs create-log-group --log-group-name "/ecs/$TASK_DEFINITION" --region $REGION
    echo "✅ CloudWatch log group created"
else
    echo "✅ CloudWatch log group already exists"
fi

# Step 4: Register task definition
echo ""
echo "📋 Step 4: Registering task definition..."
# Update task definition with account ID and region
cd "$(dirname "$0")"  # Back to aws-deployment directory
sed "s/<ACCOUNT-ID>/$ACCOUNT_ID/g; s/<REGION>/$REGION/g" task-definition.json > task-definition-updated.json
aws ecs register-task-definition --cli-input-json file://task-definition-updated.json --region $REGION
echo "✅ Task definition registered"

# Step 5: Create or update ECS cluster
echo ""
echo "🏗️  Step 5: Setting up ECS cluster..."
if ! aws ecs describe-clusters --clusters $CLUSTER_NAME --region $REGION 2>/dev/null | grep -q "$CLUSTER_NAME"; then
    aws ecs create-cluster --cluster-name $CLUSTER_NAME --region $REGION
    echo "✅ ECS cluster created"
else
    echo "✅ ECS cluster already exists"
fi

# Step 6: Get VPC and Subnet IDs (you may need to adjust these)
echo ""
echo "🌐 Step 6: Getting VPC configuration..."
VPC_ID=$(aws ec2 describe-vpcs --filters "Name=isDefault,Values=true" --query "Vpcs[0].VpcId" --output text --region $REGION)
SUBNET_IDS=$(aws ec2 describe-subnets --filters "Name=vpc-id,Values=$VPC_ID" --query "Subnets[0:2].SubnetId" --output text --region $REGION | tr '\t' ',')
SECURITY_GROUP_ID=$(aws ec2 describe-security-groups --filters "Name=vpc-id,Values=$VPC_ID" "Name=group-name,Values=default" --query "SecurityGroups[0].GroupId" --output text --region $REGION)

echo "VPC ID: $VPC_ID"
echo "Subnet IDs: $SUBNET_IDS"
echo "Security Group ID: $SECURITY_GROUP_ID"

# Step 7: Create or update ECS service
echo ""
echo "🚢 Step 7: Creating/updating ECS service..."
if aws ecs describe-services --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION 2>/dev/null | grep -q "$SERVICE_NAME"; then
    echo "Updating existing service..."
    aws ecs update-service \
        --cluster $CLUSTER_NAME \
        --service $SERVICE_NAME \
        --task-definition $TASK_DEFINITION \
        --force-new-deployment \
        --region $REGION > /dev/null
    echo "✅ Service updated"
else
    echo "Creating new service..."
    aws ecs create-service \
        --cluster $CLUSTER_NAME \
        --service-name $SERVICE_NAME \
        --task-definition $TASK_DEFINITION \
        --desired-count 1 \
        --launch-type FARGATE \
        --network-configuration "awsvpcConfiguration={subnets=[$SUBNET_IDS],securityGroups=[$SECURITY_GROUP_ID],assignPublicIp=ENABLED}" \
        --region $REGION > /dev/null
    echo "✅ Service created"
fi

# Step 8: Wait for service to stabilize
echo ""
echo "⏳ Step 8: Waiting for service to stabilize..."
aws ecs wait services-stable --cluster $CLUSTER_NAME --services $SERVICE_NAME --region $REGION
echo "✅ Service is running"

# Step 9: Get task public IP
echo ""
echo "🌍 Step 9: Getting service endpoint..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER_NAME --service-name $SERVICE_NAME --region $REGION --query "taskArns[0]" --output text)
ENI_ID=$(aws ecs describe-tasks --cluster $CLUSTER_NAME --tasks $TASK_ARN --region $REGION --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region $REGION --query "NetworkInterfaces[0].Association.PublicIp" --output text)

echo ""
echo "✅ Deployment Complete!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 API Endpoint: http://$PUBLIC_IP:5000"
echo "🏥 Health Check: http://$PUBLIC_IP:5000/health"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Next Steps:"
echo "1. Set up Application Load Balancer for better access"
echo "2. Configure custom domain with Route 53"
echo "3. Set up MongoDB Atlas connection"
echo "4. Configure security groups for production"
echo ""

