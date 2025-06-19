#!/bin/bash

echo "🔐 Generating GitHub Secrets for Catalog Server"
echo "=============================================="
echo ""

# Check if AWS CLI is configured
# if aws sts get-caller-identity >/dev/null 2>&1; then
#     echo "✅ AWS CLI is configured"
#     AWS_ACCESS_KEY_ID=$(aws configure get aws_access_key_id)
#     AWS_SECRET_ACCESS_KEY=$(aws configure get aws_secret_access_key)
#     echo "📋 AWS_ACCESS_KEY_ID: $AWS_ACCESS_KEY_ID"
#     echo "📋 AWS_SECRET_ACCESS_KEY: $AWS_SECRET_ACCESS_KEY"
# else
#     echo "❌ AWS CLI not configured. Please run: aws configure"
#     echo "   Get your keys from AWS Console → IAM → Users → Your User → Security Credentials"
#     echo ""
# fi

# Generate unique bucket name
BUCKET_NAME="catalog-server-tfstate-$(whoami)-$(date +%Y%m%d%H%M)"
echo "📦 TERRAFORM_STATE_BUCKET: $BUCKET_NAME"

# Generate database password
DB_PASSWORD="CatalogDB$(python3 -c "import secrets, string; chars = string.ascii_letters + string.digits + '!@#$%^&*'; print(''.join(secrets.choice(chars) for _ in range(12)))")!"
echo "🔒 DB_PASSWORD: $DB_PASSWORD"

# Generate Flask secret key
FLASK_SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_hex(32))")
echo "🔑 FLASK_SECRET_KEY: $FLASK_SECRET_KEY"

echo ""
echo "📝 COPY THESE VALUES TO GITHUB SECRETS:"
echo "======================================="
echo "AWS_ACCESS_KEY_ID = $AWS_ACCESS_KEY_ID"
echo "AWS_SECRET_ACCESS_KEY = $AWS_SECRET_ACCESS_KEY"
echo "TERRAFORM_STATE_BUCKET = $BUCKET_NAME"
echo "DB_PASSWORD = $DB_PASSWORD"
echo "FLASK_SECRET_KEY = $FLASK_SECRET_KEY"
echo ""
echo "⚠️  Keep these values secure and don't share them!"