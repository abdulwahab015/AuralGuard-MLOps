# 🔧 Troubleshooting Docker Build Issues

## Network Connection Errors During Build

If you see errors like:
```
ERROR: Could not install packages due to an OSError: HTTPSConnectionPool(host='files.pythonhosted.org', port=443): Max retries exceeded
```

### Quick Fixes (Try in order):

#### 1. **Check Docker Network Settings**
```bash
# Restart Docker Desktop
# macOS: Docker Desktop → Restart
# Then try building again
```

#### 2. **Build with DNS Override**
```bash
docker build --dns 8.8.8.8 --dns 8.8.4.4 -t auralguard-mlops .
```

#### 3. **Build with Network Mode**
```bash
docker build --network=host -t auralguard-mlops .
```

#### 4. **Check Internet Connection**
```bash
# Test connectivity from Docker
docker run --rm python:3.10-slim ping -c 3 files.pythonhosted.org
```

#### 5. **Use Docker BuildKit**
```bash
DOCKER_BUILDKIT=1 docker build -t auralguard-mlops .
```

#### 6. **Build in Stages (if still failing)**
```bash
# Build base image first
docker build --target base -t auralguard-base .

# Then continue with full build
docker build -t auralguard-mlops .
```

### Alternative: Build on EC2 Instead

If Docker build keeps failing locally, you can build directly on EC2:

```bash
# On EC2 instance
git clone https://github.com/abdulwahab015/AuralGuard-MLOps.git
cd AuralGuard-MLOps
docker build -t auralguard-mlops .
```

### Check Docker Desktop Settings

1. Open Docker Desktop
2. Go to Settings → Resources → Network
3. Ensure "Use kernel networking" is enabled
4. Restart Docker Desktop

### Use Alternative PyPI Mirror (Last Resort)

If PyPI is blocked, you can use a mirror. Edit Dockerfile:

```dockerfile
RUN pip install --upgrade pip setuptools wheel && \
    pip install --no-cache-dir \
        --timeout=900 \
        --retries=10 \
        --index-url https://pypi.tuna.tsinghua.edu.cn/simple \
        -r requirements.txt
```

---

## Other Common Issues

### Issue: "Permission denied" errors
```bash
# Fix Docker permissions (macOS/Linux)
sudo chmod 666 /var/run/docker.sock
# Or add user to docker group
sudo usermod -aG docker $USER
```

### Issue: "Out of disk space"
```bash
# Clean up Docker
docker system prune -a
docker volume prune
```

### Issue: Build takes too long
- The first build downloads all dependencies (can take 10-15 minutes)
- Subsequent builds use cache and are much faster
- Be patient on first build!

---

## Still Having Issues?

1. Check Docker Desktop logs
2. Try building a simple test image first:
   ```bash
   docker build -t test - <<EOF
   FROM python:3.10-slim
   RUN pip install requests
   EOF
   ```
3. If test works, the issue is specific to our dependencies
4. Try building on a different network (mobile hotspot, different WiFi)

