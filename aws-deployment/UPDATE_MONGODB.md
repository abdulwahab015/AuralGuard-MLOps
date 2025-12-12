# 🔧 Update MongoDB Connection to MongoDB Atlas

## Step 1: Get Your MongoDB Atlas Connection String (2 minutes)

### If you already have it:
- Copy your MongoDB Atlas connection string
- Format: `mongodb+srv://username:password@cluster.mongodb.net/auralguard?retryWrites=true&w=majority`
- Skip to Step 2

### If you need to get it:
1. Go to https://www.mongodb.com/cloud/atlas
2. Sign in to your account
3. Click on your cluster
4. Click "Connect" button
5. Select "Connect your application"
6. Choose:
   - **Driver:** Python
   - **Version:** 3.6 or later
7. Copy the connection string
8. **Replace `<password>` with your actual password**
9. **Add database name:** Change `/?retryWrites...` to `/auralguard?retryWrites...`

**Example:**
```
mongodb+srv://auralguard-user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/auralguard?retryWrites=true&w=majority
```

---

## Step 2: Update via AWS Console (Recommended - 5 minutes)

### Method A: Update Service Environment Variable

1. **Go to ECS Console:**
   - https://console.aws.amazon.com/ecs/
   - Click "Clusters" → `auralguard-cluster`
   - Click "Services" tab → Click `auralguard-service`

2. **Update Service:**
   - Click "Update" button (top right)
   - Scroll down to "Container overrides"
   - Click "auralguard-api" container
   - Under "Environment variables", click "Add environment variable"
   - **Key:** `MONGODB_URI`
   - **Value:** Your MongoDB Atlas connection string
   - Click "Update" button

3. **Wait for Deployment:**
   - Service will automatically deploy new tasks
   - Takes 2-3 minutes
   - Watch "Deployments" tab for progress

### Method B: Update Task Definition (More Permanent)

1. **Go to ECS Console:**
   - https://console.aws.amazon.com/ecs/
   - Click "Task Definitions" in left sidebar
   - Click `auralguard-mlops`
   - Click on latest revision (e.g., revision 4)

2. **Create New Revision:**
   - Click "Create new revision"
   - Under "Container definitions", click "auralguard-api"
   - Scroll to "Environment variables"
   - Find `MONGODB_URI` (currently: `mongodb://localhost:27017/`)
   - Click "Edit" or change value to your MongoDB Atlas connection string
   - Click "Update"

3. **Save Task Definition:**
   - Scroll to bottom
   - Click "Create" (creates new revision)

4. **Update Service:**
   - Go back to Services → `auralguard-service`
   - Click "Update"
   - Under "Task definition", select the new revision
   - Click "Update"
   - Wait for deployment

---

## Step 3: Update via Command Line (Alternative - 3 minutes)

### Quick Update (Updates Service Only):

```bash
# Set your MongoDB Atlas connection string
MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/auralguard?retryWrites=true&w=majority"

# Update service with environment variable override
aws ecs update-service \
  --cluster auralguard-cluster \
  --service auralguard-service \
  --task-definition auralguard-mlops \
  --force-new-deployment \
  --region us-east-1

# Note: This requires updating task definition first (see below)
```

### Permanent Update (Updates Task Definition):

```bash
# 1. Get current task definition
aws ecs describe-task-definition \
  --task-definition auralguard-mlops \
  --region us-east-1 \
  --query 'taskDefinition' > current-task-def.json

# 2. Edit the JSON file (replace MONGODB_URI value)
# Use your text editor or sed:
MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/auralguard?retryWrites=true&w=majority"

# 3. Register new task definition
aws ecs register-task-definition \
  --cli-input-json file://current-task-def.json \
  --region us-east-1

# 4. Update service to use new revision
aws ecs update-service \
  --cluster auralguard-cluster \
  --service auralguard-service \
  --task-definition auralguard-mlops \
  --force-new-deployment \
  --region us-east-1
```

---

## Step 4: Verify Connection (2 minutes)

### Check Logs:

```bash
# Watch logs for MongoDB connection
aws logs tail /ecs/auralguard-mlops --region us-east-1 --follow
```

**Look for:**
- ✅ "MongoDB connection initialized" = Success!
- ❌ "Could not connect to MongoDB" = Check connection string

### Test Health Endpoint:

```bash
curl http://54.164.53.192:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,  // ← Should be true now!
  "timestamp": "..."
}
```

### Test Prediction (Logs to MongoDB):

```bash
# Make a prediction (will be logged to MongoDB)
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://54.164.53.192:5000/predict
```

### Check MongoDB Atlas:

1. Go to MongoDB Atlas
2. Click "Browse Collections"
3. Database: `auralguard`
4. Collection: `predictions`
5. You should see prediction logs!

---

## 🎯 Quick Summary

**Easiest Method (AWS Console):**
1. ECS → Clusters → auralguard-cluster → Services → auralguard-service
2. Click "Update"
3. Add environment variable: `MONGODB_URI` = Your Atlas connection string
4. Click "Update"
5. Wait 2-3 minutes

**Done!** Your application will now use MongoDB Atlas for logging predictions.

---

## 🔒 Security Note

For production, consider using AWS Secrets Manager instead of environment variables:
- More secure
- Easier to rotate credentials
- Better access control

But for now, environment variable works fine!

---

## ✅ Verification Checklist

- [ ] Got MongoDB Atlas connection string
- [ ] Updated service/task definition
- [ ] New deployment started
- [ ] Health check shows `database_connected: true`
- [ ] Can see predictions in MongoDB Atlas

---

**Need help?** Check the logs if connection fails - they'll show the exact error!

