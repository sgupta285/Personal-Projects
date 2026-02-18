#!/bin/bash
# ─────────────────────────────────────────────────────────
# ClearCause MVP — Build & Deploy Script
# Usage: ./deploy.sh [dev|staging|prod]
# ─────────────────────────────────────────────────────────
set -euo pipefail

ENV="${1:-dev}"
echo "🚀 Deploying ClearCause MVP → $ENV"

# ─── 1. Package Lambda Functions ───
echo "📦 Packaging Lambda functions..."

LAMBDAS=("upload" "analyze" "report")
for fn in "${LAMBDAS[@]}"; do
    echo "  → Packaging $fn..."
    cd backend/lambdas/$fn
    
    # Create temp build dir
    rm -rf /tmp/lambda-$fn
    mkdir -p /tmp/lambda-$fn
    
    # Install dependencies
    pip install -r ../../requirements.txt -t /tmp/lambda-$fn --quiet
    
    # Copy handler
    cp handler.py /tmp/lambda-$fn/
    
    # Copy shared utilities if present
    if [ -d "../../shared" ]; then
        cp -r ../../shared /tmp/lambda-$fn/
    fi
    
    # Create zip
    cd /tmp/lambda-$fn
    zip -r9 package.zip . > /dev/null
    mv package.zip "$(dirname "$0")/backend/lambdas/$fn/package.zip" 2>/dev/null || \
    mv package.zip /tmp/lambda-$fn-package.zip
    
    cd - > /dev/null
    echo "  ✓ $fn packaged"
done

# ─── 2. Deploy Infrastructure ───
echo ""
echo "🏗️  Deploying Terraform infrastructure..."
cd infrastructure/terraform

terraform init -input=false
terraform plan -var="environment=$ENV" -out=tfplan
terraform apply -auto-approve tfplan

# Capture outputs
API_URL=$(terraform output -raw api_url)
FRONTEND_URL=$(terraform output -raw frontend_url)
COGNITO_POOL_ID=$(terraform output -raw cognito_user_pool_id)
COGNITO_CLIENT_ID=$(terraform output -raw cognito_client_id)

cd ../..

# ─── 3. Build & Deploy Frontend ───
echo ""
echo "🎨 Building frontend..."
cd frontend

# Write environment config
cat > .env.production << EOF
VITE_API_URL=$API_URL
VITE_COGNITO_USER_POOL_ID=$COGNITO_POOL_ID
VITE_COGNITO_CLIENT_ID=$COGNITO_CLIENT_ID
VITE_ENVIRONMENT=$ENV
EOF

npm ci
npm run build

echo "📤 Uploading frontend to S3..."
aws s3 sync dist/ s3://clearcause-$ENV-frontend --delete \
    --cache-control "public, max-age=31536000" \
    --exclude "index.html"

aws s3 cp dist/index.html s3://clearcause-$ENV-frontend/index.html \
    --cache-control "no-cache, no-store, must-revalidate"

cd ..

# ─── 4. Summary ───
echo ""
echo "═══════════════════════════════════════════════"
echo "✅ ClearCause MVP deployed successfully!"
echo "═══════════════════════════════════════════════"
echo "  🌐 Frontend: $FRONTEND_URL"
echo "  🔌 API:      $API_URL"
echo "  🔐 Cognito:  $COGNITO_POOL_ID"
echo "  📊 Env:      $ENV"
echo "═══════════════════════════════════════════════"
