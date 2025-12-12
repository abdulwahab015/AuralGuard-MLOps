# 📝 Step-by-Step: Update MongoDB Connection

## 🎯 Two Methods - Choose One

---

## Method 1: AWS Console (Easiest - 5 minutes) ⭐

### Step 1: Get MongoDB Atlas Connection String

1. Go to https://www.mongodb.com/cloud/atlas
2. Click your cluster → "Connect"
3. "Connect your application" → Python 3.6+
4. Copy connection string
5. Replace `<password>` with your password
6. Add database: Change `/?retryWrites` to `/auralguard?retryWrites`

**Example:**
```
mongodb+srv://username:password@cluster0.xxxxx.mongodb.net/auralguard?retryWrites=true&w=majority
```

### Step 2: Update in AWS Console

1. **Go to ECS Console:**
   - https://console.aws.amazon.com/ecs/
   - Click "Clusters" → `auralguard-cluster`
   - Click "Services" → `auralguard-service`

2. **Click "Update" button** (top right)

3. **Scroll to "Container overrides"**
   - Click on "auralguard-api" container

4. **Add Environment Variable:**
   - Click "Add environment variable"
   - **Key:** `MONGODB_URI`
   - **Value:** Paste your MongoDB Atlas connection string
   - Click "Update" (bottom)

5. **Wait 2-3 minutes** for deployment

6. **Verify:**
   ```bash
   curl http://54.164.53.192:5000/health
   ```
   Should show: `"database_connected": true`

---

## Method 2: Command Line (3 minutes)

### Step 1: Get Your MongoDB Atlas Connection String
(Same as Method 1, Step 1)

### Step 2: Run Update Script

```bash
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"

# Run the update script
./update-mongodb.sh "mongodb+srv://username:password@cluster.mongodb.net/auralguard?retryWrites=true&w=majority"
```

**Or interactively:**
```bash
./update-mongodb.sh
# Then paste your connection string when prompted
```

### Step 3: Verify

```bash
# Check health
curl http://54.164.53.192:5000/health

# Check logs
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 5m
```

---

## ✅ Verification

### 1. Health Check
```bash
curl http://54.164.53.192:5000/health
```

**Expected:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,  // ← Should be true!
  "timestamp": "..."
}
```

### 2. Check Logs
```bash
aws logs tail /ecs/auralguard-mlops --region us-east-1 --since 5m
```

**Look for:**
- ✅ "MongoDB connection initialized"
- ✅ "Database connected"

### 3. Test Prediction (Logs to MongoDB)
```bash
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://54.164.53.192:5000/predict
```

### 4. Check MongoDB Atlas
1. Go to MongoDB Atlas
2. Browse Collections → `auralguard` → `predictions`
3. You should see prediction logs!

---

## 🆘 Troubleshooting

### Issue: "database_connected": false

**Check:**
1. Connection string format is correct
2. Password is correct (no special characters need URL encoding)
3. MongoDB Atlas IP whitelist includes AWS IPs (or 0.0.0.0/0)
4. Database name is `auralguard`

### Issue: Connection timeout

**Fix:**
- MongoDB Atlas → Network Access
- Add IP: `0.0.0.0/0` (for testing) or AWS IP ranges

### Issue: Authentication failed

**Fix:**
- Check username and password
- Ensure user has read/write permissions
- URL encode special characters in password

---

## 📝 Quick Reference

**Current IP:** `54.164.53.192`  
**Health Check:** `http://54.164.53.192:5000/health`  
**API:** `http://54.164.53.192:5000`

**After update, wait 2-3 minutes for new task to start!**

