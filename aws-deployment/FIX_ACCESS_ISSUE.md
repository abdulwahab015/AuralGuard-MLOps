# 🔧 Fix "Site Can't Be Reached" - Step by Step

## Step 1: Check if Task is Running (2 minutes)

### Via AWS Console:
1. Go to: https://console.aws.amazon.com/ecs/
2. Click "Clusters" → `auralguard-cluster`
3. Click "Services" tab → Click `auralguard-service`
4. Click "Tasks" tab
5. **Check Status:**
   - ✅ Green = Running
   - ⚠️ Yellow = Pending/Starting
   - ❌ Red = Stopped/Failed

**What to look for:**
- If status is "Running" → Continue to Step 2
- If status is "Stopped" → Check "Logs" tab for errors
- If status is "Pending" → Wait 2-3 minutes

### Via Command Line:
```bash
aws ecs describe-services \
  --cluster auralguard-cluster \
  --services auralguard-service \
  --region us-east-1 \
  --query 'services[0].{RunningCount:runningCount,PendingCount:pendingCount}' \
  --output json
```

**Expected:** `RunningCount: 1`

---

## Step 2: Get Current IP Address (1 minute)

The IP address might have changed. Get the current one:

### Via AWS Console:
1. In ECS Console → Tasks tab
2. Click on the running task
3. Scroll to "Network" section
4. Copy the **Public IP** address

### Via Command Line:
```bash
TASK_ARN=$(aws ecs list-tasks --cluster auralguard-cluster --service-name auralguard-service --region us-east-1 --desired-status RUNNING --query "taskArns[0]" --output text)
ENI_ID=$(aws ecs describe-tasks --cluster auralguard-cluster --tasks $TASK_ARN --region us-east-1 --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region us-east-1 --query "NetworkInterfaces[0].Association.PublicIp" --output text)
echo "Current IP: $PUBLIC_IP"
echo "Try: http://$PUBLIC_IP:5000"
```

---

## Step 3: Fix Security Group (5 minutes) ⚠️ MOST LIKELY ISSUE

The security group probably doesn't allow inbound traffic on port 5000.

### Option A: Via AWS Console (Easiest)

1. **Go to EC2 Console:**
   - https://console.aws.amazon.com/ec2/
   - Click "Security Groups" in left sidebar

2. **Find Your Security Group:**
   - Look for: `sg-0c6b457ff0d80a10b` (or similar)
   - Or find one with description "default" or "auralguard"

3. **Add Inbound Rule:**
   - Click on the security group
   - Click "Edit inbound rules"
   - Click "Add rule"
   - **Type:** Custom TCP
   - **Port:** 5000
   - **Source:** `0.0.0.0/0` (or your specific IP for security)
   - **Description:** "AuralGuard API"
   - Click "Save rules"

4. **Test Again:**
   ```bash
   curl http://<YOUR-IP>:5000/health
   ```

### Option B: Via Command Line

```bash
# Get security group ID from your service
SG_ID=$(aws ecs describe-services \
  --cluster auralguard-cluster \
  --services auralguard-service \
  --region us-east-1 \
  --query 'services[0].networkConfiguration.awsvpcConfiguration.securityGroups[0]' \
  --output text)

echo "Security Group: $SG_ID"

# Add inbound rule for port 5000
aws ec2 authorize-security-group-ingress \
  --group-id $SG_ID \
  --protocol tcp \
  --port 5000 \
  --cidr 0.0.0.0/0 \
  --region us-east-1
```

---

## Step 4: Check Application Logs (2 minutes)

If security group is fixed but still can't access, check logs:

### Via AWS Console:
1. ECS Console → Clusters → `auralguard-cluster`
2. Services → `auralguard-service`
3. Click "Logs" tab
4. Look for errors

### Via Command Line:
```bash
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 10m
```

**Look for:**
- ✅ "Model loaded successfully" = Good
- ✅ "Starting Flask server" = Good
- ❌ "Model file not found" = Need to add model
- ❌ "Error loading model" = Model issue
- ❌ "MongoDB connection failed" = Expected (can work without it)

---

## Step 5: Verify Health Check (1 minute)

Test if the application is responding:

```bash
# Replace with your current IP
curl -v http://<YOUR-IP>:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": false,
  "timestamp": "..."
}
```

**If you get:**
- `Connection refused` = Security group issue (Step 3)
- `Connection timed out` = Security group or task not running
- `404 Not Found` = Application issue (check logs)
- `200 OK` = ✅ Working!

---

## Step 6: Check Model File (If Health Check Fails)

If health check shows `"model_loaded": false`:

1. **Model file is not in Docker image** (it's gitignored)
2. **Options:**
   - **Option A:** Add model to Docker image (rebuild)
   - **Option B:** Use EFS to mount model file
   - **Option C:** Download model from S3 at startup

**Quick fix - Rebuild with model:**
```bash
# Make sure model exists locally
ls -lh models/auralguard_model.h5

# Rebuild and push (model will be included)
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"
./deploy-ecs.sh
```

---

## Step 7: Test Full Access (2 minutes)

Once security group is fixed:

1. **Test in browser:**
   ```
   http://<YOUR-IP>:5000
   ```

2. **Test health endpoint:**
   ```bash
   curl http://<YOUR-IP>:5000/health
   ```

3. **Test prediction (if you have audio file):**
   ```bash
   curl -X POST \
     -F "audio=@test_audio.wav" \
     http://<YOUR-IP>:5000/predict
   ```

---

## 🎯 Quick Checklist

- [ ] Task is running (Step 1)
- [ ] Got current IP address (Step 2)
- [ ] Security group allows port 5000 (Step 3) ⚠️ **MOST IMPORTANT**
- [ ] Checked logs for errors (Step 4)
- [ ] Health check works (Step 5)
- [ ] Model file exists (Step 6)
- [ ] Can access in browser (Step 7)

---

## 🆘 Still Not Working?

### Common Issues:

1. **"Connection refused"**
   - ✅ Fix: Security group (Step 3)

2. **"Connection timed out"**
   - Check: Task is running
   - Check: Security group
   - Check: IP address is correct

3. **"404 Not Found"**
   - Check: Application logs
   - Check: Health check endpoint works

4. **"503 Service Unavailable"**
   - Check: Task health check
   - Check: Application is starting correctly

### Get Help:

```bash
# Get all diagnostic info
echo "=== Task Status ==="
aws ecs describe-services --cluster auralguard-cluster --services auralguard-service --region us-east-1 --query 'services[0].{Running:runningCount,Desired:desiredCount,Events:events[0].message}' --output json

echo "=== Current IP ==="
TASK_ARN=$(aws ecs list-tasks --cluster auralguard-cluster --service-name auralguard-service --region us-east-1 --desired-status RUNNING --query "taskArns[0]" --output text)
ENI_ID=$(aws ecs describe-tasks --cluster auralguard-cluster --tasks $TASK_ARN --region us-east-1 --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region us-east-1 --query "NetworkInterfaces[0].Association.PublicIp" --output text)
echo "IP: $PUBLIC_IP"

echo "=== Recent Logs ==="
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 5m | tail -20
```

---

**Most likely fix: Step 3 (Security Group)** - This is the #1 reason for "can't reach" errors! 🔒

