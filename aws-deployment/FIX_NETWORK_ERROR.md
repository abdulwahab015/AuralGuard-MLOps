# 🔧 Fix Network Connectivity Error

## Error
```
Could not connect to the endpoint URL: "https://sts.ap-southeast-2.amazonaws.com/"
```

## Possible Causes

1. **Network connectivity issue** - Can't reach AWS endpoints
2. **Region mismatch** - AWS CLI configured for different region
3. **VPN/Proxy blocking** - Corporate network blocking AWS
4. **DNS resolution issue** - Can't resolve AWS domain names

## ✅ Quick Fixes

### Fix 1: Check Internet Connection
```bash
ping google.com
ping aws.amazon.com
```

### Fix 2: Check AWS Region Configuration
```bash
aws configure get region
# Should show: us-east-1

# If wrong, set it:
aws configure set region us-east-1
```

### Fix 3: Test AWS Connectivity
```bash
# Test basic AWS connection
aws sts get-caller-identity

# If this fails, it's a network issue
```

### Fix 4: Try Different Network
- Switch to mobile hotspot
- Try different WiFi network
- Disable VPN if active

### Fix 5: Check DNS
```bash
# Test DNS resolution
nslookup sts.us-east-1.amazonaws.com
nslookup sts.ap-southeast-2.amazonaws.com
```

### Fix 6: Use Specific Region in Script
The script uses `us-east-1` but AWS CLI might be using a different default region.

**Temporarily set region:**
```bash
export AWS_DEFAULT_REGION=us-east-1
./deploy-ecs.sh
```

## 🔍 Debug Steps

1. **Check current region:**
   ```bash
   aws configure get region
   cat ~/.aws/config
   ```

2. **Test connectivity:**
   ```bash
   curl -I https://sts.us-east-1.amazonaws.com
   ```

3. **Check proxy settings:**
   ```bash
   echo $HTTP_PROXY
   echo $HTTPS_PROXY
   ```

## 🎯 Solution

Most likely, you need to:
1. **Set the correct region:**
   ```bash
   aws configure set region us-east-1
   ```

2. **Or use environment variable:**
   ```bash
   export AWS_DEFAULT_REGION=us-east-1
   export AWS_REGION=us-east-1
   ./deploy-ecs.sh
   ```

3. **Check network connectivity:**
   - Ensure you can access AWS endpoints
   - Try from different network if current one blocks AWS

## 📝 After Fixing

Once connectivity is restored:
```bash
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"
./deploy-ecs.sh
```

---

**Note:** The error shows `ap-southeast-2` (Sydney) but script uses `us-east-1`. This suggests your AWS CLI default region might be set differently.

