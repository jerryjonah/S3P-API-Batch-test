# S3P API Test Runner

A comprehensive Python terminal script for executing multiple test transactions using the Smobilpay S3P API with full authentication and transaction flow support.

## Features

- **Complete Transaction Flow**: Implements the full 4-step S3P API flow (get payment items → quote → collect → verify)
- **HMAC-SHA1 Authentication**: Uses proper HMAC-SHA1 authentication as required by the S3P API
- **Multiple Service Types**: Supports cashin, cashout, voucher, and product transactions
- **Flexible Configuration**: Command-line options for different test scenarios
- **Error Handling**: Comprehensive error handling with informative messages
- **Transaction Status Tracking**: Real-time status updates and final transaction verification
- **Batch Execution**: Execute multiple transactions in sequence with summary reporting

## Prerequisites

- Python 3.7 or higher
- `requests` library
- S3P API credentials (key and secret)

## Installation

1. Clone or download the script files
2. Install required dependencies:
```bash
pip install requests
