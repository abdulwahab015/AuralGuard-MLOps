# ⚡ AWS Quick Start Guide

## 🎯 Fastest Way to Deploy (5 minutes)

### Prerequisites
- AWS Account
- AWS CLI configured (`aws configure`)
- Model file ready (`models/auralguard_model.h5`)
- MongoDB Atlas account (free tier works)

---

## 🚀 Option 1: ECS Fargate (Recommended)

```bash
# 1. Navigate to deployment directory
cd aws-deployment

# 2. Make script executable (if not already)
chmod +x deploy-ecs.sh

# 3. Run deployment
./deploy-ecs.sh
```

**That's it!** The script will:
- Create ECR repository
- Build and push Docker image
- Set up ECS cluster and service
- Deploy your application

**Get your endpoint:** The script will output the public IP at the end.

---

## 🖥️ Option 2: EC2 (Simpler, but manual)

```bash
# 1. Launch EC2 instance (via AWS Console)
#    - Amazon Linux 2023
#    - t2.medium or larger
#    - Security Group: ports 22, 5000, 5001

# 2. Connect to EC2
ssh -i your-key.pem ec2-user@<EC2-IP>

# 3. Run these commands on EC2:
sudo yum update -y
sudo yum install docker git -y
sudo systemctl start docker
sudo systemctl enable docker
sudo usermod -aG docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Clone and deploy
git clone https://github.com/abdulwahab015/AuralGuard-MLOps.git
cd AuralGuard-MLOps

# Upload model file (from your local machine):
# scp -i your-key.pem models/auralguard_model.h5 ec2-user@<EC2-IP>:~/AuralGuard-MLOps/models/

# Set MongoDB URI
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/auralguard"

# Start services
docker-compose up -d
```

**Access your API:** `http://<EC2-PUBLIC-IP>:5000`

---

## 🔧 MongoDB Atlas Setup (2 minutes)

1. Go to [MongoDB Atlas](https://www.mongodb.com/cloud/atlas)
2. Sign up (free tier available)
3. Create a cluster (free M0 tier works)
4. Create database user
5. Get connection string: `mongodb+srv://username:password@cluster.mongodb.net/auralguard`
6. Whitelist IP: `0.0.0.0/0` (for testing) or your AWS IP ranges

---

## ✅ Verify Deployment

```bash
# Health check
curl http://<YOUR-ENDPOINT>:5000/health

# Test prediction
curl -X POST \
  -F "audio=@test_audio.wav" \
  http://<YOUR-ENDPOINT>:5000/predict
```

---

## 🆘 Troubleshooting

**Issue: Cannot connect to MongoDB**
- Check MongoDB Atlas IP whitelist
- Verify connection string format
- Test connection string locally first

**Issue: Container fails to start**
- Check CloudWatch logs (ECS) or `docker logs` (EC2)
- Verify model file exists
- Check environment variables

**Issue: High costs**
- Use t2.micro for testing (may be slow)
- Stop EC2 when not in use
- Use ECS Fargate spot instances

---

## 📚 Next Steps

- Read full guide: [AWS_DEPLOYMENT_GUIDE.md](AWS_DEPLOYMENT_GUIDE.md)
- Set up Application Load Balancer
- Configure custom domain
- Enable HTTPS
- Set up monitoring

---

**Need help?** Check the full deployment guide or open an issue on GitHub.

