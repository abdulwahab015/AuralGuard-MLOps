# 🔧 Fix DNS Resolution for AWS

## Problem
- Can resolve `google.com` ✅
- Cannot resolve `sts.us-east-1.amazonaws.com` ❌
- This suggests DNS server is blocking/filtering AWS domains

## ✅ Solutions

### Solution 1: Use Google DNS (Recommended)

**macOS:**
1. System Settings → Network
2. Select your connection (WiFi/Ethernet)
3. Click "Details" → "DNS"
4. Click "+" and add:
   - `8.8.8.8`
   - `8.8.4.4`
5. Click "OK" and reconnect

**Or via Terminal (temporary):**
```bash
# Add to /etc/resolv.conf (requires sudo)
# Or use network settings GUI
```

### Solution 2: Check Network Restrictions

Your network might be:
- Corporate/school network blocking AWS
- Firewall blocking AWS endpoints
- VPN interfering with DNS

**Try:**
1. Switch to mobile hotspot
2. Disable VPN
3. Try different network

### Solution 3: Use AWS Console Instead

If network issues persist, deploy manually via AWS Console:
- All resources are already created
- Just need to create IAM roles and update service

### Solution 4: Wait and Retry

Sometimes AWS endpoints have temporary issues:
```bash
# Wait 5 minutes and try again
sleep 300
aws sts get-caller-identity --region us-east-1
```

## 🎯 Quick Test

After changing DNS, test:
```bash
# Test DNS resolution
nslookup sts.us-east-1.amazonaws.com 8.8.8.8

# Test AWS connection
aws sts get-caller-identity --region us-east-1
```

## 📝 Current Status

✅ **What's Working:**
- Internet connection
- Basic DNS (google.com)
- AWS CLI configured
- Region set to us-east-1

❌ **What's Not Working:**
- AWS endpoint DNS resolution
- Likely network/DNS filtering

## 💡 Recommendation

**Best approach:**
1. Change DNS to Google DNS (8.8.8.8, 8.8.4.4)
2. Or switch to mobile hotspot
3. Then retry deployment

**Alternative:**
- Use AWS Console for manual deployment
- All infrastructure is ready, just need IAM roles

