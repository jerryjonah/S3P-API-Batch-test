#!/bin/bash
# S3P API Test Runner with Credentials
export S3P_KEY="1c6fbc97-c186-4091-923c-e2535fe49215"
export S3P_SECRET="2b4e01f1-7600-4152-bd91-c309e4d91fb5"

echo "🔑 S3P Credentials loaded successfully!"
echo "S3P_KEY: ${S3P_KEY:0:8}..."  # Show first 8 chars for verification
echo "S3P_SECRET: ${S3P_SECRET:0:8}..."

# Run the test (you can modify this command)
python s3p_test_runner.py --default --verbose