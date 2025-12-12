#!/bin/bash

# Complete verification script for AuralGuard deployment

echo "🔍 Verifying AuralGuard Deployment..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

REGION="us-east-1"
CLUSTER="auralguard-cluster"
SERVICE="auralguard-service"

# Get current IP
echo "📍 Getting current IP address..."
TASK_ARN=$(aws ecs list-tasks --cluster $CLUSTER --service-name $SERVICE --region $REGION --desired-status RUNNING --query "taskArns[0]" --output text 2>/dev/null)

if [ -z "$TASK_ARN" ] || [ "$TASK_ARN" == "None" ]; then
    echo "❌ No running tasks found!"
    echo "   Check ECS console for task status"
    exit 1
fi

ENI_ID=$(aws ecs describe-tasks --cluster $CLUSTER --tasks $TASK_ARN --region $REGION --query "tasks[0].attachments[0].details[?name=='networkInterfaceId'].value" --output text 2>/dev/null)
PUBLIC_IP=$(aws ec2 describe-network-interfaces --network-interface-ids $ENI_ID --region $REGION --query "NetworkInterfaces[0].Association.PublicIp" --output text 2>/dev/null)

if [ -z "$PUBLIC_IP" ]; then
    echo "❌ Could not get public IP"
    exit 1
fi

echo "   IP: $PUBLIC_IP"
echo "   URL: http://$PUBLIC_IP:5000"
echo ""

# 1. Check service status
echo "1️⃣  Checking ECS Service Status..."
SERVICE_STATUS=$(aws ecs describe-services --cluster $CLUSTER --services $SERVICE --region $REGION --query 'services[0].{Status:status,Running:runningCount,Desired:desiredCount}' --output json 2>/dev/null)
echo "$SERVICE_STATUS" | python3 -m json.tool 2>/dev/null || echo "$SERVICE_STATUS"

RUNNING=$(echo "$SERVICE_STATUS" | grep -o '"Running": [0-9]*' | grep -o '[0-9]*')
if [ "$RUNNING" == "1" ]; then
    echo "   ✅ Service is running"
else
    echo "   ⚠️  Service has $RUNNING running tasks (expected 1)"
fi
echo ""

# 2. Check health endpoint
echo "2️⃣  Checking Health Endpoint..."
HEALTH=$(curl -s --connect-timeout 5 http://$PUBLIC_IP:5000/health 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$HEALTH" ]; then
    echo "$HEALTH" | python3 -m json.tool 2>/dev/null || echo "$HEALTH"
    
    # Check key fields
    if echo "$HEALTH" | grep -q '"status": "healthy"'; then
        echo "   ✅ Status: healthy"
    fi
    
    if echo "$HEALTH" | grep -q '"model_loaded": true'; then
        echo "   ✅ Model: loaded"
    else
        echo "   ⚠️  Model: not loaded"
    fi
    
    if echo "$HEALTH" | grep -q '"database_connected": true'; then
        echo "   ✅ Database: connected"
    else
        echo "   ⚠️  Database: not connected (check MongoDB connection string)"
    fi
else
    echo "   ❌ Cannot reach health endpoint"
    echo "   Check: Security group, task status, IP address"
fi
echo ""

# 3. Check statistics
echo "3️⃣  Checking Statistics Endpoint..."
STATS=$(curl -s --connect-timeout 5 http://$PUBLIC_IP:5000/statistics 2>/dev/null)
if [ $? -eq 0 ] && [ ! -z "$STATS" ]; then
    echo "$STATS" | python3 -m json.tool 2>/dev/null || echo "$STATS"
    echo "   ✅ Statistics endpoint working"
else
    echo "   ⚠️  Statistics endpoint not accessible"
fi
echo ""

# 4. Check recent logs
echo "4️⃣  Recent Application Logs (last 10 lines):"
aws logs tail /ecs/auralguard-mlops --region $REGION --since 5m 2>/dev/null | tail -10 || echo "   ⚠️  Could not retrieve logs"
echo ""

# 5. Test web interface
echo "5️⃣  Web Interface:"
echo "   Open in browser: http://$PUBLIC_IP:5000"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ Verification Summary"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🌐 API Endpoint: http://$PUBLIC_IP:5000"
echo "🏥 Health Check: http://$PUBLIC_IP:5000/health"
echo "📊 Statistics: http://$PUBLIC_IP:5000/statistics"
echo "🔮 Predictions: http://$PUBLIC_IP:5000/predict"
echo ""
echo "📝 Next Steps:"
echo "   1. Test health endpoint in browser"
echo "   2. Try making a prediction"
echo "   3. Check MongoDB Atlas for logged predictions"
echo ""

