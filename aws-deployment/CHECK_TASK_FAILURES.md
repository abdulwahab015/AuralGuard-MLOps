# 🔍 Check Why Tasks Are Failing

## Current Status
- ✅ Service: ACTIVE
- ❌ Running Tasks: 0
- ⚠️ Tasks are starting but then failing

## 🔍 Check Task Failures

### Method 1: Check CloudWatch Logs
```bash
aws logs tail /ecs/auralguard-mlops --region us-east-1 --follow
```

### Method 2: Check Stopped Tasks
```bash
aws ecs list-tasks \
  --cluster auralguard-cluster \
  --service-name auralguard-service \
  --region us-east-1 \
  --desired-status STOPPED
```

### Method 3: Check Service Events
```bash
aws ecs describe-services \
  --cluster auralguard-cluster \
  --services auralguard-service \
  --region us-east-1 \
  --query 'services[0].events[0:5]' \
  --output table
```

### Method 4: Via AWS Console
1. Go to ECS Console
2. Clusters → auralguard-cluster
3. Services → auralguard-service
4. Click "Logs" tab
5. Or check "Events" tab for error messages

## 🎯 Common Issues

### Issue 1: IAM Roles Don't Exist
**Error:** "Unable to assume role"
**Fix:** Create IAM roles (see CREATE_IAM_ROLES.md)

### Issue 2: Model File Missing
**Error:** "Model file not found"
**Fix:** Model needs to be in the Docker image or mounted

### Issue 3: Health Check Failing
**Error:** "Health check failed"
**Fix:** Check if app is starting correctly

### Issue 4: Port/Security Group
**Error:** "Cannot reach service"
**Fix:** Check security group allows port 5000

## ✅ Quick Fix Commands

```bash
# Check what's wrong
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 1h

# Force new deployment
aws ecs update-service \
  --cluster auralguard-cluster \
  --service auralguard-service \
  --force-new-deployment \
  --region us-east-1
```

