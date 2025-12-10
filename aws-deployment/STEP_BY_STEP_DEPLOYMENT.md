# 🚀 Step-by-Step AWS Deployment Guide for Beginners

This guide will walk you through deploying AuralGuard on AWS from scratch, even if you're new to AWS.

---

## 📋 Prerequisites Checklist

Before starting, make sure you have:
- [ ] AWS Account (you have this!)
- [ ] Model file ready (`models/auralguard_model.h5`)
- [ ] Computer with terminal/command line access
- [ ] About 30-45 minutes

---

## Step 1: Set Up AWS Account & IAM User (10 minutes)

### 1.1 Create IAM User (for security best practices)

1. **Log in to AWS Console**
   - Go to https://aws.amazon.com/console/
   - Sign in with your account

2. **Navigate to IAM**
   - Search for "IAM" in the top search bar
   - Click on "IAM" service

3. **Create a New User**
   - Click "Users" in the left sidebar
   - Click "Create user" button
   - Username: `auralguard-deploy` (or any name you prefer)
   - Click "Next"

4. **Set Permissions**
   - Select "Attach policies directly"
   - Search and select these policies:
     - `AmazonEC2FullAccess` (for EC2 deployment)
     - `AmazonECS_FullAccess` (for ECS deployment)
     - `AmazonEC2ContainerRegistryFullAccess` (for Docker images)
     - `CloudWatchLogsFullAccess` (for logging)
   - Click "Next"

5. **Create User**
   - Click "Create user"
   - **IMPORTANT:** Click "Create access key"
   - Select "Command Line Interface (CLI)"
   - Check the confirmation box
   - Click "Next"
   - **SAVE THESE CREDENTIALS:**
     - Access Key ID: `AKIA...` (copy this)
     - Secret Access Key: `...` (copy this - you won't see it again!)
   - Click "Done"

**⚠️ Keep these credentials secure! Don't share them.**

---

## Step 2: Install AWS CLI (5 minutes)

### 2.1 Check if AWS CLI is installed

Open your terminal/command prompt and run:
```bash
aws --version
```

If you see a version number, skip to Step 3. If not, continue below.

### 2.2 Install AWS CLI

**For macOS:**
```bash
# Using Homebrew (recommended)
brew install awscli

# OR download installer
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /
```

**For Windows:**
- Download from: https://awscli.amazonaws.com/AWSCLIV2.msi
- Run the installer
- Follow the installation wizard

**For Linux:**
```bash
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install
```

### 2.3 Verify Installation
```bash
aws --version
# Should show: aws-cli/2.x.x
```

---

## Step 3: Configure AWS CLI (2 minutes)

### 3.1 Configure Credentials

Run this command in your terminal:
```bash
aws configure
```

You'll be prompted for 4 things:

1. **AWS Access Key ID:** 
   - Paste the Access Key ID from Step 1.5
   - Press Enter

2. **AWS Secret Access Key:**
   - Paste the Secret Access Key from Step 1.5
   - Press Enter

3. **Default region name:**
   - Type: `us-east-1` (or choose closest to you)
   - Common regions: `us-east-1`, `us-west-2`, `eu-west-1`
   - Press Enter

4. **Default output format:**
   - Type: `json`
   - Press Enter

### 3.2 Verify Configuration

Test your configuration:
```bash
aws sts get-caller-identity
```

You should see your account ID and user ARN. If you see an error, check your credentials.

---

## Step 4: Set Up MongoDB Atlas (5 minutes)

Since we'll use MongoDB Atlas (cloud database), let's set it up:

### 4.1 Create MongoDB Atlas Account

1. Go to https://www.mongodb.com/cloud/atlas
2. Click "Try Free" or "Sign Up"
3. Sign up with email or Google account

### 4.2 Create a Free Cluster

1. **Choose Cloud Provider:**
   - Select "AWS"
   - Choose region closest to your AWS region (e.g., `us-east-1`)

2. **Choose Cluster Tier:**
   - Select "M0" (Free tier - 512MB)
   - Click "Create"

3. **Wait for Cluster** (takes 3-5 minutes)
   - You'll see "Creating..." status
   - Wait until it says "Running"

### 4.3 Create Database User

1. Click "Database Access" in left sidebar
2. Click "Add New Database User"
3. **Authentication Method:** Password
4. **Username:** `auralguard-user` (or any name)
5. **Password:** Create a strong password (save it!)
6. **Database User Privileges:** "Read and write to any database"
7. Click "Add User"

### 4.4 Configure Network Access

1. Click "Network Access" in left sidebar
2. Click "Add IP Address"
3. Click "Allow Access from Anywhere" (for testing)
   - Or add specific IPs for production
4. Click "Confirm"

### 4.5 Get Connection String

1. Click "Database" in left sidebar
2. Click "Connect" on your cluster
3. Select "Connect your application"
4. **Driver:** Python
5. **Version:** 3.6 or later
6. **Copy the connection string:**
   ```
   mongodb+srv://auralguard-user:<password>@cluster0.xxxxx.mongodb.net/?retryWrites=true&w=majority
   ```
7. **Replace `<password>` with your actual password:**
   ```
   mongodb+srv://auralguard-user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/auralguard?retryWrites=true&w=majority
   ```
8. **Save this connection string** - you'll need it!

---

## Step 5: Prepare Your Project (2 minutes)

### 5.1 Navigate to Project Directory

```bash
cd "/Users/apple/Desktop/MLOps Project"
```

### 5.2 Verify Model File

Make sure your model file exists:
```bash
ls -lh models/auralguard_model.h5
```

If the file doesn't exist, you need to train the model first:
```bash
python train_and_save_model.py --epochs 10
```

### 5.3 Verify Docker is Running

```bash
docker --version
docker ps
```

If Docker is not installed:
- **macOS:** Install Docker Desktop from https://www.docker.com/products/docker-desktop
- **Windows:** Install Docker Desktop from https://www.docker.com/products/docker-desktop
- **Linux:** Follow Docker installation guide for your distribution

---

## Step 6: Choose Deployment Method

You have two options. Choose one:

### Option A: ECS Fargate (Recommended - Automated) ⭐
- **Best for:** Production, auto-scaling, managed infrastructure
- **Cost:** ~$30-40/month
- **Time:** 15-20 minutes

### Option B: EC2 (Simpler - Manual)
- **Best for:** Learning, testing, full control
- **Cost:** ~$35-45/month
- **Time:** 20-30 minutes

---

## Step 7A: Deploy to ECS Fargate (Recommended)

### 7A.1 Navigate to Deployment Directory

```bash
cd aws-deployment
```

### 7A.2 Make Script Executable

```bash
chmod +x deploy-ecs.sh
```

### 7A.3 Run Deployment Script

```bash
./deploy-ecs.sh
```

**What the script does:**
1. Creates ECR repository (for Docker images)
2. Builds your Docker image
3. Pushes image to AWS
4. Creates ECS cluster
5. Sets up ECS service
6. Deploys your application

**This takes 10-15 minutes.** You'll see progress messages.

### 7A.4 Get Your Endpoint

At the end, the script will show:
```
✅ Deployment Complete!
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🌐 API Endpoint: http://<IP-ADDRESS>:5000
🏥 Health Check: http://<IP-ADDRESS>:5000/health
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

**Save this IP address!**

### 7A.5 Configure MongoDB Connection

1. Go to AWS Console → ECS → Clusters → `auralguard-cluster`
2. Click on your service → Tasks tab
3. Click on the running task
4. Click "Configuration and tasks" tab
5. Click "Update" button
6. Under "Environment variables", add:
   - **Key:** `MONGODB_URI`
   - **Value:** Your MongoDB Atlas connection string from Step 4.5
7. Click "Update"
8. Wait for new task to start (2-3 minutes)

**OR use AWS Secrets Manager (more secure):**

```bash
# Create secret
aws secretsmanager create-secret \
  --name auralguard/mongodb-uri \
  --secret-string "mongodb+srv://user:password@cluster.mongodb.net/auralguard" \
  --region us-east-1

# Update task definition to use secret (already configured in task-definition.json)
```

---

## Step 7B: Deploy to EC2 (Alternative)

### 7B.1 Launch EC2 Instance

1. **Go to EC2 Console**
   - Search "EC2" in AWS Console
   - Click "EC2"

2. **Launch Instance**
   - Click "Launch Instance" button

3. **Configure Instance:**
   - **Name:** `auralguard-mlops`
   - **AMI:** Amazon Linux 2023 (free tier eligible)
   - **Instance type:** `t2.medium` (minimum for TensorFlow)
   - **Key pair:** Create new key pair
     - Name: `auralguard-key`
     - Key pair type: RSA
     - Private key file format: `.pem`
     - Click "Create key pair"
     - **Download the .pem file** - save it securely!
   - **Network settings:**
     - Allow SSH: Your IP
     - Allow HTTP: 0.0.0.0/0
     - Allow Custom TCP: Port 5000, Source: 0.0.0.0/0
   - **Storage:** 20 GB (default is fine)
   - Click "Launch Instance"

4. **Wait for Instance** (1-2 minutes)
   - Status will change to "Running"
   - Note the **Public IPv4 address**

### 7B.2 Connect to EC2 Instance

**On macOS/Linux:**
```bash
# Navigate to where you saved the .pem file
cd ~/Downloads  # or wherever you saved it

# Set correct permissions
chmod 400 auralguard-key.pem

# Connect to EC2
ssh -i auralguard-key.pem ec2-user@<PUBLIC-IP>
```

**On Windows:**
- Use PuTTY or Windows Subsystem for Linux (WSL)
- Or use AWS Systems Manager Session Manager

### 7B.3 Install Dependencies on EC2

Once connected to EC2, run these commands:

```bash
# Update system
sudo yum update -y

# Install Docker
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install git -y

# Log out and log back in for group changes
exit
```

**Reconnect:**
```bash
ssh -i auralguard-key.pem ec2-user@<PUBLIC-IP>
```

### 7B.4 Deploy Application

```bash
# Clone repository
git clone https://github.com/abdulwahab015/AuralGuard-MLOps.git
cd AuralGuard-MLOps

# Create models directory
mkdir -p models
```

### 7B.5 Upload Model File

**From your local machine** (in a new terminal window):

```bash
# Navigate to project directory
cd "/Users/apple/Desktop/MLOps Project"

# Upload model file
scp -i ~/Downloads/auralguard-key.pem \
    models/auralguard_model.h5 \
    ec2-user@<PUBLIC-IP>:~/AuralGuard-MLOps/models/
```

### 7B.6 Start Services

**Back on EC2** (SSH session):

```bash
# Set MongoDB connection string
export MONGODB_URI="mongodb+srv://auralguard-user:YOUR_PASSWORD@cluster0.xxxxx.mongodb.net/auralguard?retryWrites=true&w=majority"

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

Press `Ctrl+C` to exit logs. Your API is now running!

---

## Step 8: Verify Deployment (2 minutes)

### 8.1 Test Health Endpoint

```bash
# For ECS: Use the IP from Step 7A.4
curl http://<ECS-IP>:5000/health

# For EC2: Use your EC2 public IP
curl http://<EC2-IP>:5000/health
```

**Expected response:**
```json
{
  "status": "healthy",
  "model_loaded": true,
  "database_connected": true,
  "timestamp": "2025-12-10T..."
}
```

### 8.2 Test Prediction (Optional)

```bash
# Upload a test audio file
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://<YOUR-IP>:5000/predict
```

### 8.3 Access Web Interface

Open in browser:
```
http://<YOUR-IP>:5000
```

You should see the AuralGuard web interface!

---

## Step 9: Set Up Application Load Balancer (Optional - Recommended)

For production, set up an ALB for better access:

### 9.1 Create Load Balancer

1. Go to EC2 Console → Load Balancers
2. Click "Create Load Balancer"
3. Select "Application Load Balancer"
4. **Basic configuration:**
   - Name: `auralguard-alb`
   - Scheme: Internet-facing
   - IP address type: IPv4
5. **Network mapping:**
   - VPC: Default
   - Availability Zones: Select at least 2
6. **Security groups:**
   - Create new or use existing
   - Allow HTTP (port 80) from 0.0.0.0/0
7. **Listeners and routing:**
   - Protocol: HTTP, Port: 80
   - Default action: Create target group
     - Name: `auralguard-targets`
     - Target type: IP addresses
     - Protocol: HTTP, Port: 5000
     - Health check path: `/health`
8. Click "Create load balancer"

### 9.2 Register Targets

1. Go to Target Groups → `auralguard-targets`
2. Click "Register targets"
3. Enter your ECS task IP or EC2 IP
4. Click "Register targets"

### 9.3 Access via Load Balancer

Get the ALB DNS name and access:
```
http://<ALB-DNS-NAME>
```

---

## 🎉 Congratulations!

Your AuralGuard application is now deployed on AWS!

---

## 📊 Monitoring Your Deployment

### View Logs

**ECS:**
- AWS Console → CloudWatch → Log Groups → `/ecs/auralguard-mlops`

**EC2:**
```bash
ssh -i key.pem ec2-user@<IP>
docker-compose logs -f
```

### Check Costs

- AWS Console → Billing Dashboard
- Set up billing alerts to avoid surprises

---

## 🆘 Troubleshooting

### Issue: "Access Denied" errors
- Check IAM user has correct permissions
- Verify AWS credentials are correct

### Issue: Cannot connect to MongoDB
- Check MongoDB Atlas IP whitelist includes AWS IPs
- Verify connection string format
- Test connection string locally first

### Issue: Container fails to start
- Check CloudWatch logs (ECS) or `docker logs` (EC2)
- Verify model file exists
- Check environment variables

### Issue: High costs
- Stop EC2 when not in use
- Use smaller instance types for testing
- Set up billing alerts

---

## 📝 Next Steps

1. **Set up custom domain** (Route 53)
2. **Enable HTTPS** (ACM certificate)
3. **Set up auto-scaling**
4. **Configure monitoring alerts**
5. **Set up CI/CD pipeline**

---

## 💰 Cost Management

- **Stop EC2 when not in use** to save costs
- **Set up billing alerts** in AWS Console
- **Use AWS Free Tier** where possible
- **Monitor usage** in Cost Explorer

---

**Need Help?** 
- Check full guide: `AWS_DEPLOYMENT_GUIDE.md`
- AWS Support: https://aws.amazon.com/support/
- MongoDB Atlas Support: https://www.mongodb.com/support

---

**Happy Deploying! 🚀**

