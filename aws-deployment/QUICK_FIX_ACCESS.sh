#!/bin/bash

# Quick script to fix access issues

set -e

REGION="us-east-1"
CLUSTER="auralguard-cluster"
SERVICE="auralguard-service"

echo "🔍 Diagnosing access issue..."
echo ""

# Get security group
echo "1. Getting security group..."
SG_ID=$(aws ecs describe-services \
  --cluster $CLUSTER \
  --services $SERVICE \
  --region $REGION \
  --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups[0]' \
  --output text)

echo "   Security Group: $SG_ID"
echo ""

# Check if port 5000 is open
echo "2. Checking if port 5000 is open..."
PORT_OPEN=$(aws ec2 describe-security-groups \
  --group-ids $SG_ID \
  --region $REGION \
  --query 'SecurityGroups[0].IpPermissions[?FromPort==`5000`]' \
  --output json)

if [ "$PORT_OPEN" == "[]" ] || [ -z "$PORT_OPEN" ]; then
    echo "   ❌ Port 5000 is NOT open"
    echo ""
    echo "3. Opening port 5000..."
    aws ec2 authorize-security-group-ingress \
      --group-id $SG_ID \
      --protocol tcp \
      --port 5000 \
      --cidr 0.0.0.0/0 \
      --region $REGION
    
    echo "   ✅ Port 5000 is now open!"
else
    echo "   ✅ Port 5000 is already open"
fi

echo ""
echo "4. Getting current IP address..."
TASK_ARN=$(aws ecs list-tasks \
  --cluster $CLUSTER \
  --service-name $SERVICE \
  --region $REGION \
  --desired-status RUNNING \
  --query "taskArns[0]" \
  --output text)

if [ ! -z "$TASK_ARN" ] && [ "$TASK_ARN" != "None" ]; then
    ENI_ID=$(aws ecs describe-tasks \
      --cluster $CLUSTER \
      --tasks $TASK_ARN \
      --region $REGION \
      --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" \
      --output text)
    
    PUBLIC_IP=$(aws ec2 describe-network-interfaces \
      --network-interface-ids $ENI_ID \
      --region $REGION \
      --query "NetworkInterfaces[0].Association.PublicIp" \
      --output text)
    
    echo "   IP: $PUBLIC_IP"
    echo ""
    echo "✅ Your API should now be accessible at:"
    echo "   http://$PUBLIC_IP:5000"
    echo "   http://$PUBLIC_IP:5000/health"
    echo ""
    echo "Test it:"
    echo "   curl http://$PUBLIC_IP:5000/health"
else
    echo "   ⚠️  No running tasks found. Check ECS console."
fi

