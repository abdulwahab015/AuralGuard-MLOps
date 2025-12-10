#!/bin/bash

# AWS EC2 Deployment Script for AuralGuard
# This script helps deploy AuralGuard on an EC2 instance

set -e

echo "🚀 AuralGuard EC2 Deployment Helper"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Check if AWS CLI is installed
if ! command -v aws &> /dev/null; then
    echo "❌ AWS CLI is not installed. Please install it first:"
    echo "   https://aws.amazon.com/cli/"
    exit 1
fi

# Check if user is authenticated
if ! aws sts get-caller-identity &> /dev/null; then
    echo "❌ AWS CLI is not configured. Please run: aws configure"
    exit 1
fi

echo "✅ AWS CLI is configured"
echo ""

# Instructions
echo "📋 Manual Deployment Steps:"
echo ""
echo "1. Launch EC2 Instance:"
echo "   - Go to EC2 Console → Launch Instance"
echo "   - Choose: Amazon Linux 2023 or Ubuntu 22.04"
echo "   - Instance type: t2.medium (minimum)"
echo "   - Storage: 20GB"
echo "   - Security Group: Allow ports 22, 5000, 5001"
echo ""
echo "2. Connect to EC2:"
echo "   ssh -i your-key.pem ec2-user@<EC2-IP>"
echo ""
echo "3. Run these commands on EC2:"
echo ""
cat << 'EC2_COMMANDS'
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

# Clone repository
git clone https://github.com/abdulwahab015/AuralGuard-MLOps.git
cd AuralGuard-MLOps

# Create models directory and upload model file
mkdir -p models
# Then use SCP from your local machine:
# scp -i your-key.pem models/auralguard_model.h5 ec2-user@<EC2-IP>:~/AuralGuard-MLOps/models/

# Set environment variables (use MongoDB Atlas)
export MONGODB_URI="mongodb+srv://username:password@cluster.mongodb.net/auralguard"

# Start services
docker-compose up -d

# Check logs
docker-compose logs -f
EC2_COMMANDS

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📝 Environment Variables to Set:"
echo ""
echo "export MONGODB_URI='mongodb+srv://username:password@cluster.mongodb.net/auralguard'"
echo "export MONGODB_DB_NAME='auralguard'"
echo "export MONGODB_COLLECTION='predictions'"
echo "export MODEL_PATH='/app/models/auralguard_model.h5'"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔒 Security Group Configuration:"
echo "   - Port 22 (SSH): Your IP only"
echo "   - Port 5000 (API): 0.0.0.0/0 (or specific IPs)"
echo "   - Port 5001 (MLflow): 0.0.0.0/0 (optional)"
echo ""
echo "✅ After deployment, your API will be at:"
echo "   http://<EC2-PUBLIC-IP>:5000"
echo "   http://<EC2-PUBLIC-IP>:5000/health"
echo ""

