#!/usr/bin/env python3
"""
S3P API Test Runner
A comprehensive Python terminal script for executing multiple test transactions
using the Smobilpay S3P API with full authentication and transaction flow support.
"""

import requests
import hashlib
import hmac
import time
import base64
import json
import argparse
import os
import sys
import threading
import socket
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import quote, urlparse, parse_qs
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class ServiceType(Enum):
    """Supported S3P service types"""
    CASHIN = "cashin"
    CASHOUT = "cashout"
    VOUCHER = "voucher"
    PRODUCT = "product"

class TransactionStatus(Enum):
    """Transaction status values"""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    FAILED = "FAILED"
    ERROR = "ERROR"

@dataclass
class TransactionConfig:
    """Configuration for a single transaction test"""
    service_type: ServiceType
    service_id: str
    amount: int
    customer_phone: str
    customer_email: str
    customer_name: str
    customer_address: str
    service_number: str
    transaction_id: str
    webhook_url: Optional[str] = None

@dataclass
class TransactionResult:
    """Result of a transaction test"""
    config: TransactionConfig
    success: bool
    payment_item_id: Optional[str] = None
    quote_id: Optional[str] = None
    ptn: Optional[str] = None
    final_status: Optional[str] = None
    error_message: Optional[str] = None
    execution_time: Optional[float] = None
    webhook_received: bool = False
    webhook_payload: Optional[Dict] = None

class HmacService:
    """HMAC authentication service for S3P API"""
    
    def __init__(self, s3p_url: str, s3p_key: str, s3p_secret: str):
        self.s3p_url = s3p_url
        self.s3p_key = s3p_key
        self.s3p_secret = s3p_secret

    def generate_auth_header(self, http_method: str, query_params: Optional[Dict] = None, 
                           request_data: Optional[Dict] = None) -> str:
        """Generate HMAC-SHA1 authentication header for S3P API"""
        if query_params is None:
            query_params = {}
        if request_data is None:
            request_data = {}

        # Generate timestamp and nonce
        timestamp = str(int(round(time.time() * 1000)))
        nonce = str(int(round(time.time() * 1000)))

        # Construct the s3pParams dictionary
        s3p_params = {
            "s3pAuth_nonce": nonce,
            "s3pAuth_timestamp": timestamp,
            "s3pAuth_signature_method": "HMAC-SHA1",
            "s3pAuth_token": self.s3p_key
        }

        # Combine all parameters
        input_data = {**query_params, **request_data}
        params = {**input_data, **s3p_params}

        # Clean parameter values
        params = {k: (v.strip() if isinstance(v, str) else v) for k, v in params.items()}

        # Sort parameters alphabetically
        sorted_params = sorted(params.items())

        # Construct parameter string
        parameter_string = "&".join(f"{key}={str(value)}" for key, value in sorted_params)

        # Construct base string
        base_string = f"{http_method.upper()}&{quote(self.s3p_url, safe='-')}&{quote(parameter_string, safe='-')}"

        # Generate signature
        hashed = hmac.new(bytes(self.s3p_secret, "utf-8"), bytes(base_string, "utf-8"), hashlib.sha1)
        signature = base64.b64encode(hashed.digest()).decode('utf-8')

        # Construct auth header
        auth_header = (
            f's3pAuth '
            f's3pAuth_timestamp="{timestamp}", '
            f's3pAuth_signature="{signature}", '
            f's3pAuth_nonce="{nonce}", '
            f's3pAuth_signature_method="HMAC-SHA1", '
            f's3pAuth_token="{self.s3p_key}"'
        )

        return auth_header

class WebhookServer:
    """Simple HTTP server to receive S3P webhook callbacks"""
    
    def __init__(self, port: int = 0):
        self.port = port
        self.server = None
        self.thread = None
        self.webhooks_received = {}
        self.running = False
        
    def get_free_port(self) -> int:
        """Find a free port for the webhook server"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('', 0))
            s.listen(1)
            port = s.getsockname()[1]
        return port
    
    def start_server(self) -> str:
        """Start the webhook server and return the URL"""
        if self.port == 0:
            self.port = self.get_free_port()
        
        class WebhookHandler(BaseHTTPRequestHandler):
            def __init__(self, webhooks_received, *args, **kwargs):
                self.webhooks_received = webhooks_received
                super().__init__(*args, **kwargs)
            
            def do_POST(self):
                try:
                    content_length = int(self.headers.get('Content-Length', 0))
                    post_data = self.rfile.read(content_length)
                    
                    # Parse webhook payload
                    webhook_data = json.loads(post_data.decode('utf-8'))
                    
                    # Extract transaction reference
                    trid = webhook_data.get('trid') or webhook_data.get('transactionRef')
                    ptn = webhook_data.get('ptn')
                    
                    # Store webhook data
                    if trid:
                        self.webhooks_received[trid] = webhook_data
                    elif ptn:
                        self.webhooks_received[ptn] = webhook_data
                    
                    print(f"[WEBHOOK] Received callback: {json.dumps(webhook_data, indent=2)}")
                    
                    # Send response
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    self.wfile.write(b'{"status": "received"}')
                    
                except Exception as e:
                    print(f"[WEBHOOK] Error processing webhook: {e}")
                    self.send_response(500)
                    self.end_headers()
            
            def do_GET(self):
                # Health check endpoint
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "webhook server running"}')
            
            def log_message(self, format, *args):
                # Suppress default HTTP server logs
                pass
        
        # Create handler with webhook storage
        handler = lambda *args, **kwargs: WebhookHandler(self.webhooks_received, *args, **kwargs)
        
        self.server = HTTPServer(('0.0.0.0', self.port), handler)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.running = True
        
        webhook_url = f"http://0.0.0.0:{self.port}/webhook"
        print(f"[WEBHOOK] Server started on {webhook_url}")
        return webhook_url
    
    def stop_server(self):
        """Stop the webhook server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            self.running = False
            print("[WEBHOOK] Server stopped")
    
    def get_webhook_data(self, transaction_ref: str) -> Optional[Dict]:
        """Get webhook data for a transaction reference"""
        return self.webhooks_received.get(transaction_ref)
    
    def wait_for_webhook(self, transaction_ref: str, timeout: int = 60) -> Optional[Dict]:
        """Wait for webhook callback with timeout"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            webhook_data = self.get_webhook_data(transaction_ref)
            if webhook_data:
                return webhook_data
            time.sleep(1)
        return None

class S3PApiClient:
    """S3P API client with authentication and error handling"""
    
    def __init__(self, base_url: str, api_key: str, api_secret: str):
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key
        self.api_secret = api_secret
        self.session = requests.Session()
        self.session.headers.update({'Content-Type': 'application/json'})

    def _make_request(self, method: str, endpoint: str, query_params: Optional[Dict] = None, 
                     request_data: Optional[Dict] = None) -> requests.Response:
        """Make authenticated request to S3P API"""
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        hmac_service = HmacService(url, self.api_key, self.api_secret)
        
        auth_header = hmac_service.generate_auth_header(method, query_params, request_data)
        headers = {'Authorization': auth_header}
        
        if method.upper() == 'GET':
            response = self.session.get(url, headers=headers, params=query_params or {})
        elif method.upper() == 'POST':
            response = self.session.post(url, headers=headers, json=request_data or {})
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
        
        return response

    def get_payment_items(self, service_type: ServiceType, service_id: str) -> Dict[str, Any]:
        """Get payment items for a service"""
        endpoint = service_type.value
        query_params = {"serviceid": service_id}
        
        response = self._make_request("GET", endpoint, query_params=query_params)
        response.raise_for_status()
        return response.json()

    def get_quote(self, payment_item_id: str, amount: int) -> Dict[str, Any]:
        """Get quote for a payment item"""
        request_data = {
            "payItemId": payment_item_id,
            "amount": amount
        }
        
        response = self._make_request("POST", "quotestd", request_data=request_data)
        response.raise_for_status()
        return response.json()

    def execute_payment(self, quote_id: str, customer_phone: str, customer_email: str,
                       customer_name: str, customer_address: str, service_number: str,
                       transaction_id: str, webhook_url: Optional[str] = None) -> Dict[str, Any]:
        """Execute payment using quote"""
        request_data = {
            "quoteId": quote_id,
            "customerPhonenumber": customer_phone,
            "customerEmailaddress": customer_email,
            "customerName": customer_name,
            "customerAddress": customer_address,
            "serviceNumber": service_number,
            "trid": transaction_id
        }
        
        # Add webhook URL if provided
        if webhook_url:
            request_data["notificationUrl"] = webhook_url
        
        response = self._make_request("POST", "collectstd", request_data=request_data)
        response.raise_for_status()
        return response.json()

    def verify_transaction(self, ptn: str) -> Dict[str, Any]:
        """Verify transaction status"""
        query_params = {"ptn": ptn}
        
        response = self._make_request("GET", "verifytx", query_params=query_params)
        response.raise_for_status()
        return response.json()

class S3PTestRunner:
    """Main test runner for S3P API transactions"""
    
    def __init__(self, api_client: S3PApiClient, verbose: bool = False, use_webhooks: bool = False, webhook_port: int = 0):
        self.api_client = api_client
        self.verbose = verbose
        self.use_webhooks = use_webhooks
        self.webhook_server = None
        
        if self.use_webhooks:
            self.webhook_server = WebhookServer(port=webhook_port)
            self.webhook_url = self.webhook_server.start_server()

    def print_status(self, message: str, level: str = "INFO"):
        """Print status message with timestamp"""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        level_colors = {
            "INFO": "\033[36m",    # Cyan
            "SUCCESS": "\033[32m", # Green
            "ERROR": "\033[31m",   # Red
            "WARNING": "\033[33m", # Yellow
        }
        reset_color = "\033[0m"
        color = level_colors.get(level, "")
        print(f"{color}[{timestamp}] {level}: {message}{reset_color}")

    def execute_single_transaction(self, config: TransactionConfig) -> TransactionResult:
        """Execute a single transaction test"""
        start_time = time.time()
        result = TransactionResult(config=config, success=False)
        
        self.print_status(f"Starting transaction {config.transaction_id} for {config.service_type.value}")
        
        try:
            # Step 1: Get payment items
            self.print_status(f"Step 1: Getting payment items for service {config.service_id}")
            payment_items_response = self.api_client.get_payment_items(config.service_type, config.service_id)
            
            if self.verbose:
                self.print_status(f"Payment items response: {json.dumps(payment_items_response, indent=2)}")
            
            # Extract payment item ID (assuming first item for simplicity)
            if 'payItems' in payment_items_response and payment_items_response['payItems']:
                payment_item_id = payment_items_response['payItems'][0]['payItemId']
                result.payment_item_id = payment_item_id
                self.print_status(f"Found payment item ID: {payment_item_id}")
            else:
                raise Exception("No payment items found in response")

            # Step 2: Get quote
            self.print_status(f"Step 2: Getting quote for amount {config.amount}")
            quote_response = self.api_client.get_quote(payment_item_id, config.amount)
            
            if self.verbose:
                self.print_status(f"Quote response: {json.dumps(quote_response, indent=2)}")
            
            if 'quoteId' in quote_response:
                quote_id = quote_response['quoteId']
                result.quote_id = quote_id
                self.print_status(f"Received quote ID: {quote_id}")
            else:
                raise Exception("No quote ID found in response")

            # Step 3: Execute payment
            self.print_status(f"Step 3: Executing payment")
            webhook_url = config.webhook_url or (self.webhook_url if self.use_webhooks else None)
            if webhook_url:
                self.print_status(f"Using webhook URL: {webhook_url}")
            
            payment_response = self.api_client.execute_payment(
                quote_id, config.customer_phone, config.customer_email,
                config.customer_name, config.customer_address, 
                config.service_number, config.transaction_id, webhook_url
            )
            
            if self.verbose:
                self.print_status(f"Payment response: {json.dumps(payment_response, indent=2)}")
            
            if 'ptn' in payment_response:
                ptn = payment_response['ptn']
                result.ptn = ptn
                self.print_status(f"Payment initiated with PTN: {ptn}")
            else:
                raise Exception("No PTN found in payment response")

            # Step 4: Wait for webhook or poll for status
            if webhook_url and self.webhook_server:
                self.print_status("Step 4: Waiting for webhook callback...")
                webhook_data = self.webhook_server.wait_for_webhook(config.transaction_id, timeout=120)
                
                if webhook_data:
                    result.webhook_received = True
                    result.webhook_payload = webhook_data
                    result.final_status = webhook_data.get('status', 'UNKNOWN')
                    
                    if result.final_status == TransactionStatus.SUCCESS.value:
                        result.success = True
                        self.print_status(f"Transaction {config.transaction_id} completed successfully via webhook!", "SUCCESS")
                    else:
                        self.print_status(f"Transaction {config.transaction_id} status from webhook: {result.final_status}", "WARNING")
                else:
                    self.print_status("No webhook received, falling back to polling", "WARNING")
                    # Fall back to polling
                    time.sleep(20)
                    verify_response = self.api_client.verify_transaction(ptn)
                    if 'status' in verify_response:
                        result.final_status = verify_response['status']
                        if result.final_status == TransactionStatus.SUCCESS.value:
                            result.success = True
            else:
                # Traditional polling approach
                wait_times = {
                    ServiceType.CASHIN: 20,
                    ServiceType.CASHOUT: 120,
                    ServiceType.VOUCHER: 20,
                    ServiceType.PRODUCT: 20
                }
                wait_time = wait_times.get(config.service_type, 20)
                
                self.print_status(f"Step 4: Waiting {wait_time} seconds before verification")
                time.sleep(wait_time)
                
                self.print_status("Verifying transaction status")
                verify_response = self.api_client.verify_transaction(ptn)
            
                if self.verbose:
                    self.print_status(f"Verification response: {json.dumps(verify_response, indent=2)}")
                
                # Extract final status from polling
                if 'status' in verify_response:
                    final_status = verify_response['status']
                    result.final_status = final_status
                    
                    if final_status == TransactionStatus.SUCCESS.value:
                        result.success = True
                        self.print_status(f"Transaction {config.transaction_id} completed successfully!", "SUCCESS")
                    elif final_status == TransactionStatus.PENDING.value:
                        self.print_status(f"Transaction {config.transaction_id} is still pending", "WARNING")
                    else:
                        self.print_status(f"Transaction {config.transaction_id} failed with status: {final_status}", "ERROR")
                else:
                    raise Exception("No status found in verification response")

        except requests.exceptions.RequestException as e:
            error_msg = f"API request failed: {str(e)}"
            result.error_message = error_msg
            self.print_status(error_msg, "ERROR")
        except Exception as e:
            error_msg = f"Transaction failed: {str(e)}"
            result.error_message = error_msg
            self.print_status(error_msg, "ERROR")
        
        result.execution_time = time.time() - start_time
        return result

    def execute_multiple_transactions(self, configs: List[TransactionConfig]) -> List[TransactionResult]:
        """Execute multiple transaction tests"""
        results = []
        
        self.print_status(f"Starting execution of {len(configs)} transactions")
        if self.use_webhooks:
            self.print_status("Webhook mode enabled - using callbacks for status updates")
        
        for i, config in enumerate(configs, 1):
            self.print_status(f"\n=== Transaction {i}/{len(configs)} ===")
            result = self.execute_single_transaction(config)
            results.append(result)
            
            # Small delay between transactions
            if i < len(configs):
                time.sleep(2)
        
        # Stop webhook server if running
        if self.webhook_server:
            self.webhook_server.stop_server()
        
        # Print summary
        self.print_summary(results)
        return results

    def print_summary(self, results: List[TransactionResult]):
        """Print execution summary"""
        self.print_status("\n=== EXECUTION SUMMARY ===")
        
        successful = sum(1 for r in results if r.success)
        failed = len(results) - successful
        
        self.print_status(f"Total transactions: {len(results)}")
        self.print_status(f"Successful: {successful}", "SUCCESS" if successful > 0 else "INFO")
        self.print_status(f"Failed: {failed}", "ERROR" if failed > 0 else "INFO")
        
        # Webhook statistics
        webhook_received = sum(1 for r in results if r.webhook_received)
        if webhook_received > 0:
            self.print_status(f"Webhook callbacks received: {webhook_received}")
        
        if failed > 0:
            self.print_status("\nFailed transactions:")
            for result in results:
                if not result.success:
                    self.print_status(f"  - {result.config.transaction_id}: {result.error_message or 'Unknown error'}", "ERROR")

def create_default_configs() -> List[TransactionConfig]:
    """Create default test configurations"""
    return [
        TransactionConfig(
            service_type=ServiceType.CASHIN,
            service_id="20052",
            amount=1000,
            customer_phone="237655754334",
            customer_email="test@smobilpay.com",
            customer_name="Test Customer",
            customer_address="Test Address, Douala",
            service_number="677389120",
            transaction_id=f"test_cashin_{int(time.time())}"
        ),
        TransactionConfig(
            service_type=ServiceType.CASHOUT,
            service_id="20053",
            amount=500,
            customer_phone="237655754334",
            customer_email="test@smobilpay.com",
            customer_name="Test Customer",
            customer_address="Test Address, Douala",
            service_number="677389120",
            transaction_id=f"test_cashout_{int(time.time())}"
        ),
        TransactionConfig(
            service_type=ServiceType.PRODUCT,
            service_id="90006",
            amount=2000,
            customer_phone="237655754334",
            customer_email="test@smobilpay.com",
            customer_name="Test Customer",
            customer_address="Test Address, Douala",
            service_number="23900419411616",
            transaction_id=f"test_product_{int(time.time())}"
        )
    ]

def load_config_from_file(file_path: str) -> List[TransactionConfig]:
    """Load transaction configurations from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        configs = []
        for item in data:
            config = TransactionConfig(
                service_type=ServiceType(item['service_type']),
                service_id=item['service_id'],
                amount=item['amount'],
                customer_phone=item['customer_phone'],
                customer_email=item['customer_email'],
                customer_name=item['customer_name'],
                customer_address=item['customer_address'],
                service_number=item['service_number'],
                transaction_id=item['transaction_id']
            )
            configs.append(config)
        
        return configs
    except Exception as e:
        print(f"Error loading config file: {e}")
        sys.exit(1)

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="S3P API Test Runner - Execute multiple test transactions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python s3p_test_runner.py --default
  python s3p_test_runner.py --config transactions.json --verbose
  python s3p_test_runner.py --single cashin 20052 1000 --verbose
  python s3p_test_runner.py --default --webhook --verbose
  python s3p_test_runner.py --single cashin 20052 1000 test_001 --webhook --webhook-port 8080
        """
    )
    
    # API credentials
    parser.add_argument('--url', default=os.getenv('S3P_URL', 'https://s3p.smobilpay.staging.maviance.info/v2'),
                       help='S3P API base URL')
    parser.add_argument('--key', default=os.getenv('S3P_KEY', ''),
                       help='S3P API key')
    parser.add_argument('--secret', default=os.getenv('S3P_SECRET', ''),
                       help='S3P API secret')
    
    # Execution modes
    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument('--default', action='store_true',
                           help='Run default test configurations')
    mode_group.add_argument('--config', metavar='FILE',
                           help='Load configurations from JSON file')
    mode_group.add_argument('--single', nargs=4, metavar=('SERVICE_TYPE', 'SERVICE_ID', 'AMOUNT', 'TRANSACTION_ID'),
                           help='Run single transaction test')
    
    # Options
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose output')
    parser.add_argument('--webhook', action='store_true',
                       help='Enable webhook mode for real-time status updates')
    parser.add_argument('--webhook-port', type=int, default=0,
                       help='Port for webhook server (0 = auto-assign)')
    
    args = parser.parse_args()
    
    # Validate credentials
    if not args.key or not args.secret:
        print("Error: S3P API key and secret are required. Set via --key/--secret or S3P_KEY/S3P_SECRET environment variables.")
        sys.exit(1)
    
    # Initialize API client
    api_client = S3PApiClient(args.url, args.key, args.secret)
    test_runner = S3PTestRunner(api_client, verbose=args.verbose, use_webhooks=args.webhook, webhook_port=args.webhook_port)
    
    # Determine configurations
    configs = []
    if args.default:
        configs = create_default_configs()
    elif args.config:
        configs = load_config_from_file(args.config)
    elif args.single:
        service_type, service_id, amount, transaction_id = args.single
        config = TransactionConfig(
            service_type=ServiceType(service_type),
            service_id=service_id,
            amount=int(amount),
            customer_phone="237655754334",
            customer_email="test@smobilpay.com",
            customer_name="Test Customer",
            customer_address="Test Address, Douala",
            service_number="677389120",
            transaction_id=transaction_id
        )
        configs = [config]
    
    # Execute transactions
    try:
        results = test_runner.execute_multiple_transactions(configs)
        
        # Exit with error code if any transaction failed
        if any(not r.success for r in results):
            sys.exit(1)
    except KeyboardInterrupt:
        print("\nExecution interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"Execution failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
