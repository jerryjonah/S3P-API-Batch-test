#!/bin/bash

# S3P Production Test Runner
# Streamlined script for testing core money transfer services

echo "🏭 S3P Production Test Runner"
echo "Testing core services: Cashin, Cashout, Topup"
echo "========================================"

# Check if credentials are set
if [ -z "$S3P_KEY" ] || [ -z "$S3P_SECRET" ]; then
    echo "❌ Error: S3P credentials not found!"
    echo "Please set environment variables:"
    echo "export S3P_KEY=\"your-s3p-api-key\""
    echo "export S3P_SECRET=\"your-s3p-api-secret\""
    exit 1
fi

# Display credentials (masked for security)
echo "🔑 S3P Credentials loaded successfully!"
echo "S3P_KEY: ${S3P_KEY:0:8}..."
echo "S3P_SECRET: ${S3P_SECRET:0:8}..."
echo ""

# Run production tests
python s3p_production_runner.py --all --verbose

# Check exit code
if [ $? -eq 0 ]; then
    echo ""
    echo "✅ All production tests completed successfully!"
else
    echo ""
    echo "❌ Some production tests failed. Check the output above for details."
    exit 1
fi