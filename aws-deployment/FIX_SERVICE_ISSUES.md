# 🔧 Fix ECS Service Issues

## Problem
Service was created but tasks are not running (0 running tasks).

## Root Causes
1. **Missing IAM Roles** - Task definition references roles that don't exist
2. **Missing MongoDB Secret** - Task definition references secret that doesn't exist
3. **Tasks failing to start** - Need to check CloudWatch logs

## ✅ Quick Fix

### Option 1: Update Task Definition (Recommended)

The task definition has been updated to:
- Remove IAM role requirements (use default)
- Use environment variable instead of secret for MongoDB

**Run this to update:**

```bash
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"

# Update task definition
ACCOUNT_ID=$(aws sts get-caller-identity --query Account --output text)
REGION="us-east-1"
sed "s/<ACCOUNT-ID>/$ACCOUNT_ID/g; s/<REGION>/$REGION/g" task-definition.json > task-definition-updated.json

# Register new task definition
aws ecs register-task-definition --cli-input-json file://task-definition-updated.json --region $REGION

# Force new deployment
aws ecs update-service \
  --cluster auralguard-cluster \
  --service auralguard-service \
  --force-new-deployment \
  --region $REGION
```

### Option 2: Create Required IAM Roles

If you want to use IAM roles (more secure):

```bash
# Create execution role
aws iam create-role \
  --role-name ecsTaskExecutionRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'

# Attach policy
aws iam attach-role-policy \
  --role-name ecsTaskExecutionRole \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

# Create task role (optional)
aws iam create-role \
  --role-name ecsTaskRole \
  --assume-role-policy-document '{
    "Version": "2012-10-17",
    "Statement": [{
      "Effect": "Allow",
      "Principal": {"Service": "ecs-tasks.amazonaws.com"},
      "Action": "sts:AssumeRole"
    }]
  }'
```

### Option 3: Set MongoDB URI via Environment Variable

Update the service to add MongoDB URI:

```bash
# Get your MongoDB Atlas connection string first
# Then update the service:

aws ecs update-service \
  --cluster auralguard-cluster \
  --service auralguard-service \
  --task-definition auralguard-mlops \
  --force-new-deployment \
  --region us-east-1

# Then add environment variable via AWS Console:
# ECS → Clusters → auralguard-cluster → Services → auralguard-service
# → Update → Add environment variable: MONGODB_URI
```

## 🔍 Check What's Wrong

### View Service Events
```bash
aws ecs describe-services \
  --cluster auralguard-cluster \
  --services auralguard-service \
  --region us-east-1 \
  --query 'services[0].events[0:5]' \
  --output table
```

### View CloudWatch Logs
```bash
aws logs tail /ecs/auralguard-mlops --region us-east-1 --follow
```

### Check Task Status
```bash
aws ecs list-tasks --cluster auralguard-cluster --service-name auralguard-service --region us-east-1
```

## 🎯 Recommended Next Steps

1. **Update task definition** (Option 1 above) - Simplest fix
2. **Set MongoDB URI** - Add it as environment variable in service
3. **Check logs** - See what errors are happening
4. **Wait 2-3 minutes** - Tasks take time to start

## 📝 After Fixing

Once tasks are running:
1. Get task IP address
2. Test health endpoint
3. Update MongoDB URI if needed

