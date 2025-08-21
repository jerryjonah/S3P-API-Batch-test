# S3P API Test Runner

## Overview

The S3P API Test Runner is a comprehensive Python terminal application designed to execute automated test transactions using the Smobilpay S3P API. The system implements a complete 4-step transaction flow (get payment items → quote → collect → verify) with proper HMAC-SHA1 authentication. It supports multiple service types including cashin, cashout, voucher, and product transactions, providing flexible configuration options for different test scenarios and batch execution capabilities with summary reporting.

## User Preferences

Preferred communication style: Simple, everyday language.

## System Architecture

### Core Application Structure
The application follows a modular Python architecture with three main components:
- **Main Runner** (`s3p_test_runner.py`): Core transaction processing engine implementing the complete S3P API flow
- **Configuration Module** (`config.py`): Centralized configuration management with default service settings and test data
- **HMAC Service** (`attached_assets/s3p_cashout_1755778294633.py`): Authentication utility for generating proper HMAC-SHA1 signatures

### Authentication Architecture
The system implements HMAC-SHA1 authentication as required by the S3P API:
- **Signature Generation**: Uses timestamp-based nonces and parameter sorting for consistent signature creation
- **Request Signing**: All API requests are signed with proper authentication headers
- **Security**: Credentials (key and secret) are managed through environment variables or configuration

### Transaction Flow Architecture
The application implements a stateful 4-step transaction process:
1. **Payment Items Retrieval**: Fetches available payment options for the specified service
2. **Quote Generation**: Requests transaction quotes with customer and service details
3. **Collection Process**: Executes the actual transaction using the generated quote
4. **Verification**: Confirms final transaction status and completion

### Data Models
The system uses Python dataclasses and enums for type safety:
- **ServiceType Enum**: Defines supported service categories (cashin, cashout, voucher, product)
- **TransactionStatus Enum**: Tracks transaction states (pending, success, failed, error)
- **TransactionConfig**: Encapsulates all transaction parameters and customer data
- **TransactionResult**: Stores execution results and status information

### Error Handling Strategy
Comprehensive error handling with multiple layers:
- **API Response Validation**: Checks HTTP status codes and response structure
- **Transaction Status Monitoring**: Real-time tracking of transaction progression
- **Retry Logic**: Built-in retry mechanisms for transient failures
- **Informative Messaging**: Detailed error messages for debugging and troubleshooting

### Configuration Management
Flexible configuration system supporting:
- **Default Service Configurations**: Pre-configured settings for each service type with sample data
- **Customer Data Templates**: Reusable customer information for testing
- **Amount Recommendations**: Suggested transaction amounts per service type
- **Command-Line Overrides**: Runtime configuration through CLI arguments

## External Dependencies

### Required Python Libraries
- **requests**: HTTP client library for API communication with the S3P service
- **hashlib**: Cryptographic hashing for HMAC signature generation
- **hmac**: HMAC authentication implementation for API security
- **base64**: Encoding utilities for authentication headers

### S3P API Integration
- **Smobilpay S3P API**: Primary external service for payment processing
- **Authentication**: Requires valid S3P API credentials (key and secret)
- **Endpoints**: Integrates with multiple S3P API endpoints for complete transaction flow
- **Protocol**: REST API communication over HTTPS

### System Dependencies
- **Python 3.7+**: Minimum Python version requirement for modern language features
- **Terminal/CLI Environment**: Designed for command-line execution and interaction
- **Network Connectivity**: Requires internet access for API communication