import requests
import hashlib
import hmac
import time
import base64
from urllib.parse import quote, urlencode
 
class HmacService:
    def __init__(self, s3p_url, s3p_key, s3p_secret):
        self.s3p_url = s3p_url
        self.s3p_key = s3p_key
        self.s3p_secret = s3p_secret
 
    def generate_auth_header(self, http_method, query_params=None, request_data=None):
        if query_params is None:
            query_params = {}
        if request_data is None:
            request_data = {}
 
        # Generate timestamp in milliseconds
        timestamp = str(int(round(time.time() * 1000)))
        nonce = str(int(round(time.time() * 1000)))  # Use the same value for simplic
 
        # Construct the s3pParams dictionary
        s3p_params = {
            "s3pAuth_nonce": nonce,
            "s3pAuth_timestamp": timestamp,
            "s3pAuth_signature_method": "HMAC-SHA1",
            "s3pAuth_token": self.s3p_key
        }
 
        # Combine query parameters and request body
        input_data = {**query_params, **request_data}
 
        # Combine input data and s3pParams
        params = {**input_data, **s3p_params}
 
        # Remove any leading/trailing whitespace from parameter values
        params = {k: (v.strip() if isinstance(v, str) else v) for k, v in params.items()}
 
        # Sort the parameters alphabetically by key
 
        sorted_params = sorted(params.items())
        #print(f"Sorted Params:\n{sorted_params}")
 
        # Construct the parameter string
        parameter_string = "&".join(f"{key}={str(value)}" for key, value in sorted_params)
 
         #print(f"parameter_string:\n{parameter_string}")
 
        # Construct the base string with the correct HTTP method
        base_string = f"{http_method.upper()}&{quote(self.s3p_url, safe='-')}&{quote(parameter_string, safe='-')}"
 
        # Generate the signature using HMAC-SHA1 and self.s3p_secret
        hashed = hmac.new(bytes(self.s3p_secret, "utf-8"), bytes(base_string, "utf-8"), hashlib.sha1)
        signature = base64.b64encode(hashed.digest()).decode('utf-8')
 
        # Construct the auth_header according to the JavaScript example format
        auth_header = (
            f's3pAuth '
            f's3pAuth_timestamp="{timestamp}", '
            f's3pAuth_signature="{signature}", '
            f's3pAuth_nonce="{nonce}", '
            f's3pAuth_signature_method="HMAC-SHA1", '
            f's3pAuth_token="{self.s3p_key}"'
        )
 
        return auth_header
 
 
# Example usage:
if __name__ == "__main__":
    # Replace with your actual values
    s3p_key = "1c6fbc97-c186-4091-923c-e2535fe49215"
    s3p_secret = "2b4e01f1-7600-4152-bd91-c309e4d91fb5"
 
    #Get Cashout Service
    s3p_url = "https://s3p.smobilpay.staging.maviance.info/v2/cashout"
 
    # Initialize the HmacService
    hmac_service = HmacService(s3p_url, s3p_key, s3p_secret)
 
    # Example: Generate auth header for a request
    query_params = {}
    request_data = {}
    http_method = "GET"
 
    auth_header_all_services = hmac_service.generate_auth_header(http_method, query_params, request_data)
    print(f"Generated Auth Header:\n{auth_header_all_services}")
 
     # Make API request with generated authorization header
    headers = {
        'Authorization': auth_header_all_services,
        'Content-Type': 'application/json'
    }
 
    response = requests.get(s3p_url, headers=headers)
 
    # Print response
    print('Response of Get Services:', response.text)
 
 
 
    #Get Cashout Service
    s3p_url = "https://s3p.smobilpay.staging.maviance.info/v2/cashout"
 
    # Initialize the HmacService
    hmac_service = HmacService(s3p_url, s3p_key, s3p_secret)
 
    # Example: Generate auth header for a request
    query_params = {"serviceid": "50053"}
    request_data = {}
    http_method = "GET"
 
    auth_header_cashout_service = hmac_service.generate_auth_header(http_method, query_params, request_data)
    print(f"Generated Auth Header:\n{auth_header_cashout_service}")
 
     # Make API request with generated authorization header
    headers = {
        'Authorization': auth_header_cashout_service,
        'Content-Type': 'application/json'
    }
 
    response = requests.get(s3p_url, headers=headers, params=query_params)
 
    # Print response
    print('Response of Get Cashout Service:', response.text)
 
 
 
    #Get the quoteId
    s3p_url_quote = "https://s3p.smobilpay.staging.maviance.info/v2/quotestd"
    hmac_service_quote = HmacService(s3p_url_quote, s3p_key, s3p_secret)
    query_params = {}
    request_data_quote = {
        "payItemId": "S-112-949-CMORANGEMOMO-50053-900221-1",
        "amount": 100
    }
    http_method_quote = "POST"
    auth_header_quote = hmac_service_quote.generate_auth_header(http_method_quote, query_params, request_data_quote)
    headers_quote = {
        'Authorization': auth_header_quote,
        'Content-Type': 'application/json'
    }
    response_quote = requests.post(s3p_url_quote, headers=headers_quote, json=request_data_quote)
    print('Response from quotestd:', response_quote.text)
   
 
    # Extract quoteId from Quote response
    response_data_quote = response_quote.json()
    print('response_data_quote:', response_data_quote)
    quoteId = response_data_quote.get("quoteId")
 
 
 
 
    #Use the quoteId for collectstd
    s3p_url_collect = "https://s3p.smobilpay.staging.maviance.info/v2/collectstd"
    hmac_service_collect = HmacService(s3p_url_collect, s3p_key, s3p_secret)
 
     #print('quoteid:', quoteId)
    request_data_collect = {
        "quoteId": quoteId,
        "customerPhonenumber": "237654905897",
        "customerEmailaddress": "qas3p@yopmail.com",
        "customerName": "QA S3P",
        "customerAddress": "Mambanda Bonaberi",
        "serviceNumber": "698081976",
        "trid": "Jay-test-Cashout005"
    }
    http_method_collect = "POST"
    auth_header_collect = hmac_service_collect.generate_auth_header(http_method_collect, query_params, request_data_collect)
    headers_collect = {
        'Authorization': auth_header_collect,
        'Content-Type': 'application/json'
    }
    response_collect = requests.post(s3p_url_collect, headers=headers_collect, json=request_data_collect)
     #print(f"Generated Auth Header:\n{auth_header_collect}")
 
    # Print response
    print('Response from collectstd:', response_collect.text)
 
 
 
    # Extract PTN from the collect response
    response_data_collect = response_collect.json()
    print('response_data_collect:', response_data_collect)
    ptn = response_data_collect.get("ptn")
 
 
 
 
    #Get status of transaction
    time.sleep(30)
    s3p_url = "https://s3p.smobilpay.staging.maviance.info/v2/verifytx"
 
    # Initialize the HmacService
    hmac_service = HmacService(s3p_url, s3p_key, s3p_secret)
 
    # Example: Generate auth header for a request
    query_params = {"ptn": ptn}
    request_data = {}
    http_method = "GET"
 
    auth_header = hmac_service.generate_auth_header(http_method, query_params, request_data)
    print(f"Generated Auth Header:\n{auth_header}")
 
     # Make API request with generated authorization header
    headers = {
        'Authorization': auth_header,
        'Content-Type': 'application/json'
    }
 
    response = requests.get(s3p_url, headers=headers, params=query_params)
 
    # Print response
    print('Response of verify transaction status:', response.text)