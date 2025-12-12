# ✅ Verify Everything is Working - Complete Checklist

## 🎯 Quick Verification (2 minutes)

### Step 1: Check Health Endpoint
```bash
curl http://54.164.53.192:5000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "timestamp": "2025-12-12T..."
}
```

**What to check:**
- ✅ `status: "healthy"` = API is running
- ✅ `model_loaded: true` = Model is loaded
- ✅ `database_connected: true` = MongoDB is connected

### Step 2: Test Web Interface
Open in browser:
```
http://54.164.53.192:5000
```

**Expected:**
- ✅ See AuralGuard web interface
- ✅ Can upload audio file
- ✅ Can make predictions

---

## 📊 Detailed Verification

### 1. Check ECS Service Status

**Via Command Line:**
```bash
aws ecs describe-services \
  --cluster auralguard-cluster \
  --services auralguard-service \
  --region us-east-1 \
  --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' \
  --output json
```

**Expected:**
```json
{
  "Status": "ACTIVE",
  "Running": 1,
  "Desired": 1
}
```

**Via AWS Console:**
1. Go to: https://console.aws.amazon.com/ecs/v2/clusters/auralguard-cluster/services/auralguard-service?region=us-east-1
2. Check:
   - ✅ Service status: ACTIVE
   - ✅ Running tasks: 1
   - ✅ Desired tasks: 1

### 2. Check Task is Running

**Via Command Line:**
```bash
aws ecs list-tasks \
  --cluster auralguard-cluster \
  --service-name auralguard-service \
  --region us-east-1 \
  --desired-status RUNNING
```

**Expected:** Should return a task ARN

**Via AWS Console:**
- ECS → Clusters → auralguard-cluster → Services → auralguard-service
- Click "Tasks" tab
- ✅ Should see task with status "Running" (green)

### 3. Check Application Logs

```bash
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 10m
```

**Look for:**
- ✅ "Model loaded successfully"
- ✅ "MongoDB connection initialized"
- ✅ "Starting Flask server"
- ✅ "Running on http://0.0.0.0:5000"

**No errors should appear!**

### 4. Test Health Endpoint (Detailed)

```bash
curl -v http://54.164.53.192:5000/health
```

**Expected:**
- ✅ HTTP 200 OK
- ✅ JSON response with all fields
- ✅ `model_loaded: true`
- ✅ `database_connected: true`

### 5. Test Prediction Endpoint

**If you have an audio file:**
```bash
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://54.164.53.192:5000/predict
```

**Expected Response:**
```json
{
  "prediction": "real",
  "probability": 0.9234,
  "confidence": 0.8468,
  "filename": "test_audio.wav",
  "processing_time_seconds": 0.1234,
  "timestamp": "2025-12-12T..."
}
```

### 6. Check Statistics Endpoint

```bash
curl http://54.164.53.192:5000/statistics
```

**Expected:**
```json
{
  "total_predictions": 1,
  "real_predictions": 1,
  "fake_predictions": 0,
  "real_percentage": 100.0,
  "fake_percentage": 0.0
}
```

### 7. Check MongoDB Atlas

1. **Go to:** https://www.mongodb.com/cloud/atlas
2. **Click:** "Browse Collections"
3. **Check:**
   - ✅ Database: `auralguard` exists
   - ✅ Collection: `predictions` exists
   - ✅ Documents: Should see prediction logs after making predictions

### 8. Check Recent Predictions

```bash
curl http://54.164.53.192:5000/predictions?limit=5
```

**Expected:**
```json
{
  "predictions": [
    {
      "timestamp": "...",
      "audio_filename": "...",
      "prediction_probability": 0.9234,
      "predicted_label": "real",
      ...
    }
  ],
  "count": 1
}
```

---

## 🎯 Complete Verification Script

Run this to check everything at once:

```bash
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"

cat << 'EOF' > verify-deployment.sh
#!/bin/bash

echo "🔍 Verifying AuralGuard Deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Get current IP
TASK_ARN=$(aws ecs list-tasks --cluster auralguard-cluster --service-name auralguard-service --region us-east-1 --desired-status RUNNING --query "taskArns[0]" --output text)
ENI_ID=$(aws ecs describe-tasks --cluster auralguard-cluster --tasks $TASK_ARN --region us-east-1 --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region us-east-1 --query "NetworkInterfaces[0].Association.PublicIp" --output text)

echo "📍 API Endpoint: http://$PUBLIC_IP:5000"
echo ""

# 1. Check service status
echo "1️⃣  Checking ECS Service..."
SERVICE_STATUS=$(aws ecs describe-services --cluster auralguard-cluster --services auralguard-service --region us-east-1 --query 'services[0].{Status:status,Running:runningCount}' --output json)
echo "$SERVICE_STATUS"
echo ""

# 2. Check health
echo "2️⃣  Checking Health Endpoint..."
HEALTH=$(curl -s http://$PUBLIC_IP:5000/health)
echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
echo ""

# 3. Check statistics
echo "3️⃣  Checking Statistics..."
STATS=$(curl -s http://$PUBLIC_IP:5000/statistics)
echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
echo ""

# 4. Check recent logs
echo "4️⃣  Recent Logs (last 5 lines):"
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 5m | tail -5
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Verification complete!"
echo ""
echo "🌐 Access your API: http://$PUBLIC_IP:5000"
EOF

chmod +x verify-deployment.sh
./verify-deployment.sh
```

---

## ✅ Success Checklist

- [ ] ECS service is ACTIVE
- [ ] Task is RUNNING
- [ ] Health endpoint returns 200 OK
- [ ] `model_loaded: true` in health response
- [ ] `database_connected: true` in health response
- [ ] Web interface loads in browser
- [ ] Can make predictions (if you have audio file)
- [ ] Statistics endpoint works
- [ ] Predictions endpoint works
- [ ] MongoDB Atlas shows prediction logs
- [ ] No errors in CloudWatch logs

---

## 🆘 If Something Fails

### Health Check Fails
- Check CloudWatch logs for errors
- Verify task is running
- Check security group allows port 5000

### Model Not Loaded
- Model file might not be in Docker image
- Check logs for "Model file not found"
- May need to rebuild Docker image with model

### Database Not Connected
- Check MongoDB connection string is correct
- Verify MongoDB Atlas IP whitelist
- Check logs for connection errors

### Can't Access API
- Verify security group allows port 5000
- Check task is running
- Get current IP (it might have changed)

---

## 🎉 Everything Working?

If all checks pass:
- ✅ Your MLOps application is fully deployed!
- ✅ API is accessible
- ✅ Model is working
- ✅ MongoDB is logging predictions
- ✅ Ready for submission!

**Congratulations!** 🚀

