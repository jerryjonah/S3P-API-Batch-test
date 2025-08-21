"""
Configuration module for S3P API Test Runner
Contains default configurations and helper functions for managing test data.
"""

from typing import Dict, List, Optional
from s3p_test_runner import TransactionConfig, ServiceType

# Default service configurations based on Postman collection
DEFAULT_SERVICES = {
    ServiceType.CASHIN: {
        "service_id": "20052",
        "sample_pay_item_id": "S-112-948-CMORANGEOM-30052-2006125104-1"
    },
    ServiceType.CASHOUT: {
        "service_id": "20053", 
        "sample_pay_item_id": "S-112-949-MTNMOMO-20053-200050001-1"
    },
    ServiceType.VOUCHER: {
        "service_id": "2000",
        "sample_pay_item_id": "S-112-974-CMENEOPREPAID-2000-10010-1"
    },
    ServiceType.PRODUCT: {
        "service_id": "90006",
        "sample_pay_item_id": "S-112-952-CMStarTimes-90006-900210-1"
    },
    ServiceType.SUBSCRIPTION: {
        "service_id": "5000",
        "sample_pay_item_id": "S-112-953-CMSABC-5000-500001-1"
    },
    ServiceType.TOPUP: {
        "service_id": "20062",
        "sample_pay_item_id": "S-112-954-TOPUP-20062-100001-1"
    }
}

# Default customer data for testing
DEFAULT_CUSTOMER_DATA = {
    "phone": "237655754334",
    "email": "test@smobilpay.com", 
    "name": "Test Customer",
    "address": "Test Address, Douala, Cameroon"
}

# Default service numbers for different service types
DEFAULT_SERVICE_NUMBERS = {
    ServiceType.CASHIN: "677389120",
    ServiceType.CASHOUT: "677389120", 
    ServiceType.VOUCHER: "677777777",
    ServiceType.PRODUCT: "23900419411616",
    ServiceType.SUBSCRIPTION: "00000108",
    ServiceType.TOPUP: "698081976"
}

# Recommended amounts for different service types (in local currency)
RECOMMENDED_AMOUNTS = {
    ServiceType.CASHIN: [500, 1000, 2000, 5000],
    ServiceType.CASHOUT: [500, 1000, 2000],
    ServiceType.VOUCHER: [1000, 2000, 5000],
    ServiceType.PRODUCT: [2000, 5000, 10000],
    ServiceType.SUBSCRIPTION: [1000, 2000, 3000],
    ServiceType.TOPUP: [100, 500, 1000, 2000]
}

def create_test_config(service_type: ServiceType, amount: Optional[int] = None, 
                      transaction_id: Optional[str] = None) -> TransactionConfig:
    """Create a test configuration for a specific service type"""
    import time
    
    if amount is None:
        amount = RECOMMENDED_AMOUNTS[service_type][0]
    
    if transaction_id is None:
        timestamp = int(time.time())
        transaction_id = f"test_{service_type.value}_{timestamp}"
    
    return TransactionConfig(
        service_type=service_type,
        service_id=DEFAULT_SERVICES[service_type]["service_id"],
        amount=amount,
        customer_phone=DEFAULT_CUSTOMER_DATA["phone"],
        customer_email=DEFAULT_CUSTOMER_DATA["email"],
        customer_name=DEFAULT_CUSTOMER_DATA["name"],
        customer_address=DEFAULT_CUSTOMER_DATA["address"],
        service_number=DEFAULT_SERVICE_NUMBERS[service_type],
        transaction_id=transaction_id
    )

def create_comprehensive_test_suite() -> List[TransactionConfig]:
    """Create a comprehensive test suite covering all service types and amounts"""
    configs = []
    
    for service_type in ServiceType:
        for amount in RECOMMENDED_AMOUNTS[service_type][:2]:  # Test first 2 amounts
            config = create_test_config(service_type, amount)
            configs.append(config)
    
    return configs

def create_stress_test_suite(count: int = 10) -> List[TransactionConfig]:
    """Create a stress test suite with multiple transactions of the same type"""
    import time
    configs = []
    
    for i in range(count):
        timestamp = int(time.time()) + i
        config = TransactionConfig(
            service_type=ServiceType.CASHIN,
            service_id=DEFAULT_SERVICES[ServiceType.CASHIN]["service_id"],
            amount=1000,
            customer_phone=DEFAULT_CUSTOMER_DATA["phone"],
            customer_email=DEFAULT_CUSTOMER_DATA["email"],
            customer_name=f"{DEFAULT_CUSTOMER_DATA['name']} {i+1}",
            customer_address=DEFAULT_CUSTOMER_DATA["address"],
            service_number=DEFAULT_SERVICE_NUMBERS[ServiceType.CASHIN],
            transaction_id=f"stress_test_{timestamp}_{i+1}"
        )
        configs.append(config)
    
    return configs
