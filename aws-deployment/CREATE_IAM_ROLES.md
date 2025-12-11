# 🔐 Create IAM Roles via AWS Console

Your IAM user doesn't have permission to create roles. Create them via AWS Console:

## Step 1: Create Execution Role (Required)

1. **Go to IAM Console:**
   - https://console.aws.amazon.com/iam/
   - Click "Roles" → "Create role"

2. **Select Trust Entity:**
   - Select "AWS service"
   - Choose "Elastic Container Service"
   - Select "Elastic Container Service Task"

3. **Add Permissions:**
   - Search and select: `AmazonECSTaskExecutionRolePolicy`
   - Click "Next"

4. **Name the Role:**
   - Role name: `ecsTaskExecutionRole`
   - Click "Create role"

## Step 2: Create Task Role (Optional but Recommended)

1. **Create Another Role:**
   - Click "Roles" → "Create role"

2. **Select Trust Entity:**
   - Select "AWS service"
   - Choose "Elastic Container Service"
   - Select "Elastic Container Service Task"

3. **Skip Permissions:**
   - Click "Next" (no policies needed)

4. **Name the Role:**
   - Role name: `ecsTaskRole`
   - Click "Create role"

## Step 3: Update Your IAM User (Optional)

To allow script to create roles in future, add to your IAM user:
- Policy: `IAMFullAccess` (or create custom policy with `iam:CreateRole`, `iam:AttachRolePolicy`)

## Step 4: Re-run Deployment

After creating roles:

```bash
cd "/Users/apple/Desktop/MLOps Project/aws-deployment"
./deploy-ecs.sh
```

The script will now find the roles and tasks should start successfully!

---

**Quick Links:**
- IAM Console: https://console.aws.amazon.com/iam/
- ECS Console: https://console.aws.amazon.com/ecs/

