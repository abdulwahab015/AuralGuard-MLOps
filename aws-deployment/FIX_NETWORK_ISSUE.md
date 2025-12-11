# 🔧 Fix Network Issue During Docker Build

## Problem
The Docker build is failing when trying to download `librosa` from PyPI due to network connectivity issues.

## ✅ Solution Applied

I've updated the Dockerfile to:
1. ✅ Use `requirements.txt` instead of individual package installs
2. ✅ Increased retries (10, then 15 on retry)
3. ✅ Added trusted hosts for PyPI
4. ✅ Added fallback retry mechanism
5. ✅ Added `requests` to requirements.txt (needed for healthcheck)

## 🚀 Try Building Again

### Option 1: Simple Retry (Recommended)
```bash
cd "/Users/apple/Desktop/MLOps Project"
docker build -t auralguard-mlops .
```

The updated Dockerfile now has better retry logic, so it should work on retry.

### Option 2: Restart Docker Desktop First
1. **Restart Docker Desktop** (this often fixes network issues)
2. Then try building:
   ```bash
   cd "/Users/apple/Desktop/MLOps Project"
   docker build -t auralguard-mlops .
   ```

### Option 3: Build with BuildKit
```bash
cd "/Users/apple/Desktop/MLOps Project"
DOCKER_BUILDKIT=1 docker build -t auralguard-mlops .
```

### Option 4: Check Your Network
The error suggests DNS resolution issues. Try:
```bash
# Test if you can reach PyPI
ping files.pythonhosted.org

# If that fails, check your internet connection
ping google.com
```

### Option 5: Use Mobile Hotspot
Sometimes corporate/school networks block PyPI. Try:
1. Connect to mobile hotspot
2. Restart Docker Desktop
3. Try building again

## 📝 What Changed

**Before:**
- Installing packages in batches manually
- Limited retries (5 attempts)
- No fallback mechanism

**After:**
- Using `requirements.txt` (better dependency resolution)
- 10 retries, then 15 on second attempt
- Trusted hosts configured
- Fallback retry built-in

## ⏱️ Expected Build Time

- **First build:** 10-15 minutes (downloads all packages)
- **Subsequent builds:** 2-3 minutes (uses cache)

## 🆘 Still Failing?

If it still fails after trying the above:

1. **Check Docker Desktop logs:**
   - Docker Desktop → Troubleshoot → View logs

2. **Try building on EC2 instead:**
   - The network on AWS EC2 is usually more reliable
   - Follow EC2 deployment guide

3. **Build without cache:**
   ```bash
   docker build --no-cache -t auralguard-mlops .
   ```

4. **Check if it's a specific package:**
   - The error was on `librosa`
   - Try installing it locally first: `pip install librosa`
   - If that fails, it's a network/DNS issue

## ✅ Next Steps After Successful Build

Once the build succeeds:
```bash
# Test the image locally
docker run -p 5000:5000 auralguard-mlops

# Then continue with ECS deployment
cd aws-deployment
./deploy-ecs.sh
```

---

**The updated Dockerfile should handle network issues much better now!** 🚀

