# S3P API Test Runner

A comprehensive Python terminal application for executing automated test transactions using the Smobilpay S3P API. The system implements a complete 4-step transaction flow with proper HMAC-SHA1 authentication, supports 6 service types, includes webhook functionality for real-time status updates, and generates Excel reports.

## ✅ Supported Services

| Service | Status | Description | Available Amounts |
|---------|--------|-------------|-------------------|
| **CASHIN** | ✅ Working | MTN Mobile Money Cash-in | Custom amounts (500-5000 XAF) |
| **CASHOUT** | ✅ Working | MTN Mobile Money Cash-out | Custom amounts (500-2000 XAF) |
| **TOPUP** | ✅ Working | Orange Airtime Top-up | Custom amounts (100-2000 XAF) |
| **PRODUCT** | ✅ Working | Canal+ TV Packages | Fixed: 10K, 15K, 22.5K, 45K XAF |
| **SUBSCRIPTION** | ✅ Working | SABC Subscription Bills | Custom amounts (1000-3000 XAF) |
| **BILL** | ✅ Working | ENEO Electricity Bills | Custom amounts (500-5000 XAF) |

## 🚀 Quick Start

### Prerequisites

- **Python 3.7+** (required)
- **pip** (Python package manager)
- **S3P API Credentials** (key and secret)

### Step 1: Download and Setup

```bash
# Clone or download the project files
# Ensure you have these files:
# - s3p_test_runner.py
# - config.py
# - run_tests.sh
# - requirements.txt (if available)

# Navigate to the project directory
cd s3p-test-runner
```

### Step 2: Install Dependencies

```bash
# Install required Python packages
pip install requests openpyxl

# Or if you have requirements.txt:
pip install -r requirements.txt
```

### Step 3: Set Environment Variables

Create a `.env` file or set environment variables:

```bash
# Option 1: Environment variables (recommended)
export S3P_KEY="your-s3p-api-key"
export S3P_SECRET="your-s3p-api-secret"
export S3P_URL="https://s3p.smobilpay.staging.maviance.info/v2"

# Option 2: Use command line arguments (see usage below)
```

### Step 4: Make Scripts Executable (Linux/Mac)

```bash
chmod +x run_tests.sh
```

## 📋 Usage Examples

### Run All Service Tests (Default)

```bash
# Test all 6 services with default configurations
./run_tests.sh

# Or with explicit credentials:
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --default
```

### Single Service Testing

```bash
# Test individual services
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --single cashin 20052 1000 JAYTEST123456789012345 --verbose

# Available service types:
# - cashin: MTN Mobile Money deposits
# - cashout: MTN Mobile Money withdrawals  
# - topup: Orange airtime purchases
# - product: Canal+ TV packages (use: 10000, 15000, 22500, or 45000)
# - subscription: SABC bill payments
# - bill: ENEO electricity bill payments
```

### Service-Specific Examples

```bash
# Canal+ TV Package (10K EVASION package)
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --single product 90006 10000 JAYPRODUCT123456789012345 --verbose

# ENEO Bill Payment  
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --single bill 10039 1000 JAYBILL123456789012345 --verbose

# MTN Mobile Money Cash-in
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --single cashin 20052 500 JAYCASHIN123456789012345 --verbose
```

### With Webhook Support

```bash
# Enable real-time webhook notifications
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --default --webhook --verbose

# Custom webhook port
S3P_KEY="your-key" S3P_SECRET="your-secret" python s3p_test_runner.py --single topup 20062 500 JAYTOPUP123456789012345 --webhook --webhook-port 8080 --verbose
```

## 🔧 Configuration

### Transaction ID Requirements

- Must start with "JAY"
- Minimum 21 characters total
- Must be unique per transaction
- Example: `JAYCASHIN17557830153015`

### Service-Specific Configuration

**Product Service (Canal+):**
- Only accepts fixed amounts: 10000, 15000, 22500, 45000 XAF
- Each amount corresponds to different Canal+ packages
- Custom amounts will fail

**BILL Service (ENEO):**
- Service ID: 10039
- Merchant: ENEO
- Service Number: 203157530 (fixed)

**Subscription Service (SABC):**
- Service ID: 5000
- Merchant: CMSABC
- Customer Number: 00000108 (fixed)

## 📊 Output and Reports

### Excel Reports

After each execution, an Excel report is automatically generated:

- **Filename**: `s3p_transaction_report_YYYYMMDD_HHMMSS.xlsx`
- **Contains**: Service ID, Amount, Service Type, Service Number, PTN, Transaction ID, Status, Error Messages
- **Location**: Same directory as the script

### Console Output

The script provides detailed console output including:

- Transaction progress (4-step flow)
- API request/response details (with `--verbose`)
- Real-time status updates
- Success/failure summary
- Webhook notifications (if enabled)

## 🛠 Troubleshooting

### Common Issues

**1. Import Error: No module named 'requests'**
```bash
pip install requests openpyxl
```

**2. Authentication Failed**
- Verify your S3P API credentials
- Check environment variables are set correctly
- Ensure credentials have proper permissions

**3. Product Service Failed with Custom Amount**
- Use only fixed amounts: 10000, 15000, 22500, or 45000 XAF
- Canal+ packages require exact predefined amounts

**4. Webhook Server Port Already in Use**
```bash
# Use a different port
python s3p_test_runner.py --default --webhook --webhook-port 8081
```

### Debugging

Enable verbose output to see detailed API communication:

```bash
python s3p_test_runner.py --single cashin 20052 1000 JAYTEST123456789012345 --verbose
```

## 🔐 Security Notes

- **Never commit API credentials** to version control
- Store credentials in environment variables or secure configuration files
- Use HTTPS endpoints only (default configuration)
- Transaction IDs should be unique to prevent duplicates

## 📝 Advanced Usage

### Custom Configuration File

Create a JSON configuration file for batch testing:

```json
[
  {
    "service_type": "cashin",
    "service_id": "20052",
    "amount": 1000,
    "customer_phone": "237655754334",
    "customer_email": "test@example.com",
    "customer_name": "Test Customer",
    "customer_address": "Test Address",
    "service_number": "677389120",
    "transaction_id": "JAYCASHIN123456789012345"
  }
]
```

```bash
python s3p_test_runner.py --config transactions.json --verbose
```

### Environment-Specific URLs

```bash
# Staging environment (default)
export S3P_URL="https://s3p.smobilpay.staging.maviance.info/v2"

# Production environment (when available)
export S3P_URL="https://s3p.smobilpay.maviance.info/v2"
```

## 📞 Support

For S3P API-related issues, contact Smobilpay support.

For script-related issues:
1. Check console output with `--verbose` flag
2. Verify all dependencies are installed
3. Ensure API credentials are valid
4. Review transaction ID format requirements

## 🎯 Success Criteria

A successful transaction shows:
- ✅ Payment items retrieved
- ✅ Quote generated  
- ✅ Payment executed (PTN received)
- ✅ Transaction verified with SUCCESS status
- ✅ Excel report generated with PTN

Example successful output:
```
[2025-08-21 13:40:28] SUCCESS: Transaction JAYPRODUCTTEST10K123456789 completed successfully!
PTN: 99999175578360700092855294564747
Excel report generated: s3p_transaction_report_20250821_134028.xlsx
```