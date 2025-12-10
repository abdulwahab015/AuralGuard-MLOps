# 🚀 AWS Deployment Guide for AuralGuard

This guide covers multiple AWS deployment options for the AuralGuard MLOps project.

## 📋 Prerequisites

- AWS Account
- AWS CLI installed and configured (`aws configure`)
- Docker installed locally
- Model file (`models/auralguard_model.h5`) ready
- MongoDB Atlas account (recommended) or AWS DocumentDB

---

## 🎯 Deployment Options

### Option 1: AWS ECS with Fargate (Recommended) ⭐
**Best for:** Production deployments, auto-scaling, managed infrastructure
**Cost:** ~$15-30/month (depending on usage)

### Option 2: AWS EC2 (Simple)
**Best for:** Quick deployment, full control, learning
**Cost:** ~$10-20/month (t2.medium instance)

### Option 3: AWS Elastic Beanstalk
**Best for:** Easy deployment, managed platform
**Cost:** Free tier available, then pay for resources

---

## 🚀 Option 1: AWS ECS with Fargate (Recommended)

### Step 1: Push Docker Image to ECR

```bash
# 1. Create ECR repository
aws ecr create-repository --repository-name auralguard-mlops --region us-east-1

# 2. Get login token
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <account-id>.dkr.ecr.us-east-1.amazonaws.com

# 3. Build and tag image
docker build -t auralguard-mlops .
docker tag auralguard-mlops:latest <account-id>.dkr.ecr.us-east-1.amazonaws.com/auralguard-mlops:latest

# 4. Push to ECR
docker push <account-id>.dkr.ecr.us-east-1.amazonaws.com/auralguard-mlops:latest
```

### Step 2: Set Up MongoDB Atlas (Recommended)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Create a free cluster
3. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/auralguard`
4. Whitelist AWS IP ranges or use `0.0.0.0/0` for testing

### Step 3: Create ECS Task Definition

Use the provided `task-definition.json` file (see below) or create via AWS Console.

### Step 4: Create ECS Cluster and Service

```bash
# Create cluster
aws ecs create-cluster --cluster-name auralguard-cluster --region us-east-1

# Create service (see deploy-ecs.sh script)
./deploy-ecs.sh
```

### Step 5: Set Up Application Load Balancer

1. Create ALB in AWS Console
2. Create target group pointing to ECS service
3. Configure health check: `/health`
4. Get public DNS name

**Your API will be available at:** `http://<alb-dns-name>/`

---

## 🖥️ Option 2: AWS EC2 (Simple Deployment)

### Step 1: Launch EC2 Instance

1. Go to EC2 Console → Launch Instance
2. Choose: **Amazon Linux 2023** or **Ubuntu 22.04 LTS**
3. Instance type: **t2.medium** or larger (for TensorFlow)
4. Storage: 20GB minimum
5. Security Group: Allow ports 22 (SSH), 5000 (API), 5001 (MLflow)
6. Launch and connect via SSH

### Step 2: Install Dependencies on EC2

```bash
# Connect to EC2
ssh -i your-key.pem ec2-user@<ec2-ip>

# Install Docker
sudo yum update -y
sudo yum install docker -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install Git
sudo yum install git -y
```

### Step 3: Deploy Application

```bash
# Clone repository
git clone https://github.com/abdulwahab015/AuralGuard-MLOps.git
cd AuralGuard-MLOps

# Upload model file (use SCP from local machine)
# scp -i your-key.pem models/auralguard_model.h5 ec2-user@<ec2-ip>:~/AuralGuard-MLOps/models/

# Set up MongoDB Atlas connection string
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/auralguard"

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
```

### Step 4: Configure Security Group

1. EC2 Console → Security Groups
2. Edit inbound rules:
   - Port 5000: Allow from `0.0.0.0/0` (or specific IPs)
   - Port 5001: Allow from `0.0.0.0/0` (MLflow UI)

**Your API will be available at:** `http://<ec2-public-ip>:5000/`

---

## ☁️ Option 3: AWS Elastic Beanstalk

### Step 1: Install EB CLI

```bash
pip install awsebcli
```

### Step 2: Initialize Elastic Beanstalk

```bash
eb init -p docker auralguard-mlops --region us-east-1
eb create auralguard-env
```

### Step 3: Configure Environment Variables

```bash
eb setenv MONGODB_URI="mongodb+srv://..." \
         MONGODB_DB_NAME=auralguard \
         MODEL_PATH=/app/models/auralguard_model.h5
```

### Step 4: Deploy

```bash
eb deploy
eb open
```

---

## 🔧 Configuration Files

### Environment Variables

```bash
# Required
MONGODB_URI=mongodb+srv://username:password@cluster.mongodb.net/auralguard
MONGODB_DB_NAME=auralguard
MONGODB_COLLECTION=predictions
MODEL_PATH=/app/models/auralguard_model.h5

# Optional
PORT=5000
FLASK_DEBUG=False
MLFLOW_TRACKING_URI=file:/app/mlruns
```

### Security Best Practices

1. **Use AWS Secrets Manager** for MongoDB credentials
2. **Use IAM roles** instead of access keys
3. **Enable VPC** for ECS/EC2
4. **Use HTTPS** with Application Load Balancer
5. **Restrict security groups** to specific IPs

---

## 📊 Monitoring & Logging

### CloudWatch Logs

ECS and EC2 automatically send logs to CloudWatch:
- Log Group: `/ecs/auralguard` or `/aws/ec2/auralguard`

### CloudWatch Metrics

Monitor:
- CPU utilization
- Memory usage
- Request count
- Error rate

### Set Up Alarms

```bash
aws cloudwatch put-metric-alarm \
  --alarm-name auralguard-high-cpu \
  --alarm-description "Alert when CPU > 80%" \
  --metric-name CPUUtilization \
  --namespace AWS/ECS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold
```

---

## 💰 Cost Estimation

### ECS Fargate (Recommended)
- **Task (0.5 vCPU, 1GB RAM)**: ~$15/month
- **Application Load Balancer**: ~$16/month
- **Data Transfer**: ~$0.09/GB
- **Total**: ~$30-40/month

### EC2
- **t2.medium instance**: ~$30/month
- **EBS storage (20GB)**: ~$2/month
- **Data Transfer**: ~$0.09/GB
- **Total**: ~$35-45/month

### MongoDB Atlas
- **Free tier**: 512MB storage
- **M0 Cluster**: Free (good for testing)
- **M10 Cluster**: ~$57/month (production)

---

## 🚨 Troubleshooting

### Issue: Container fails to start
- Check CloudWatch logs
- Verify environment variables
- Ensure model file exists in container

### Issue: Cannot connect to MongoDB
- Verify MongoDB Atlas IP whitelist
- Check connection string format
- Test connection from local machine first

### Issue: High memory usage
- Increase task memory allocation
- Optimize model loading
- Consider model quantization

### Issue: Slow predictions
- Use GPU instances (g4dn.xlarge)
- Enable model caching
- Optimize audio preprocessing

---

## 📝 Next Steps

1. Set up CI/CD with GitHub Actions
2. Configure auto-scaling
3. Set up custom domain with Route 53
4. Enable HTTPS with ACM certificate
5. Implement monitoring dashboards

---

## 🔗 Useful Links

- [AWS ECS Documentation](https://docs.aws.amazon.com/ecs/)
- [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
- [AWS Pricing Calculator](https://calculator.aws/)

---

**Need Help?** Check the deployment scripts in this directory or open an issue on GitHub.

