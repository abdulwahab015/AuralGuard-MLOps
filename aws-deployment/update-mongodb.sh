#!/bin/bash

# Script to update MongoDB connection string in ECS service

set -e

REGION="us-east-1"
CLUSTER="auralguard-cluster"
SERVICE="auralguard-service"
TASK_DEF="auralguard-mlops"

echo "🔧 Update MongoDB Connection String"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get MongoDB URI from user
if [ -z "$1" ]; then
    echo "Usage: ./update-mongodb.sh 'mongodb+srv://user:pass@cluster.mongodb.net/auralguard'"
    echo ""
    echo "Or enter your MongoDB Atlas connection string:"
    read -p "MongoDB URI: " MONGODB_URI
else
    MONGODB_URI="$1"
fi

if [ -z "$MONGODB_URI" ]; then
    echo "❌ MongoDB URI is required"
    exit 1
fi

echo "📝 Updating task definition..."
echo ""

# Get current task definition
CURRENT_REV=$(aws ecs describe-task-definition \
    --task-definition $TASK_DEF \
    --region $REGION \
    --query 'taskDefinition.revision' \
    --output text)

echo "Current revision: $CURRENT_REV"

# Get full task definition
aws ecs describe-task-definition \
    --task-definition $TASK_DEF \
    --region $REGION \
    --query 'taskDefinition' > /tmp/task-def.json

# Update MONGODB_URI in task definition
python3 << EOF
import json
import sys

with open('/tmp/task-def.json', 'r') as f:
    task_def = json.load(f)

# Find and update MONGODB_URI
for env_var in task_def['containerDefinitions'][0]['environment']:
    if env_var['name'] == 'MONGODB_URI':
        env_var['value'] = '$MONGODB_URI'
        break
else:
    # Add if not found
    task_def['containerDefinitions'][0]['environment'].append({
        'name': 'MONGODB_URI',
        'value': '$MONGODB_URI'
    })

# Remove fields that shouldn't be in register-task-definition
for field in ['taskDefinitionArn', 'revision', 'status', 'requiresAttributes', 'compatibilities', 'registeredAt', 'registeredBy']:
    task_def.pop(field, None)

with open('/tmp/task-def-updated.json', 'w') as f:
    json.dump(task_def, f, indent=2)
EOF

# Register new task definition
echo "Registering new task definition..."
NEW_REV=$(aws ecs register-task-definition \
    --cli-input-json file:///tmp/task-def-updated.json \
    --region $REGION \
    --query 'taskDefinition.revision' \
    --output text)

echo "✅ New revision: $NEW_REV"
echo ""

# Update service
echo "Updating service..."
aws ecs update-service \
    --cluster $CLUSTER \
    --service $SERVICE \
    --task-definition $TASK_DEF:$NEW_REV \
    --force-new-deployment \
    --region $REGION > /dev/null

echo "✅ Service updated"
echo ""
echo "⏳ Waiting for new deployment (this takes 2-3 minutes)..."
aws ecs wait services-stable \
    --cluster $CLUSTER \
    --services $SERVICE \
    --region $REGION

echo ""
echo "✅ Deployment complete!"
echo ""
echo "Test the connection:"
echo "  curl http://54.164.53.192:5000/health"
echo ""
echo "Check logs:"
echo "  aws logs tail /ecs/auralguard-mlops --region $REGION --follow"

