#!/usr/bin/env python3
"""
Bank QR Payment Integration for MyMurid
Supports multiple Malaysian banks and payment providers
"""

import requests
import json
import hashlib
import hmac
import time
from datetime import datetime, timezone, timedelta
from typing import Dict, Optional, Tuple

class BankQRPayment:
    """Bank QR Payment Integration"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.base_url = config.get('base_url')
        self.merchant_id = config.get('merchant_id')
        self.api_key = config.get('api_key')
        self.secret_key = config.get('secret_key')
        self.callback_url = config.get('callback_url')
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate QR payment request"""
        
        # Prepare payment data
        payment_data = {
            'merchant_id': self.merchant_id,
            'transaction_id': transaction_id,
            'amount': f"{amount:.2f}",
            'currency': 'MYR',
            'description': description,
            'callback_url': self.callback_url,
            'timestamp': int(time.time()),
            'return_url': f"{self.callback_url}?status=success&txn_id={transaction_id}",
            'cancel_url': f"{self.callback_url}?status=cancelled&txn_id={transaction_id}"
        }
        
        # Generate signature
        signature = self._generate_signature(payment_data)
        payment_data['signature'] = signature
        
        try:
            # Make API request
            response = requests.post(
                f"{self.base_url}/api/v1/qr/generate",
                json=payment_data,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {self.api_key}',
                    'X-Merchant-ID': self.merchant_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'qr_code': result.get('qr_code'),
                    'qr_data': result.get('qr_data'),
                    'payment_url': result.get('payment_url'),
                    'expires_at': result.get('expires_at'),
                    'reference_id': result.get('reference_id')
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code} - {response.text}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Network Error: {str(e)}"
            }
    
    def check_payment_status(self, transaction_id: str) -> Dict:
        """Check payment status"""
        
        try:
            response = requests.get(
                f"{self.base_url}/api/v1/payment/status/{transaction_id}",
                headers={
                    'Authorization': f'Bearer {self.api_key}',
                    'X-Merchant-ID': self.merchant_id
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'amount': result.get('amount'),
                    'paid_at': result.get('paid_at'),
                    'reference_id': result.get('reference_id')
                }
            else:
                return {
                    'success': False,
                    'error': f"API Error: {response.status_code}"
                }
                
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': f"Network Error: {str(e)}"
            }
    
    def _generate_signature(self, data: Dict) -> str:
        """Generate HMAC signature for API security"""
        # Sort parameters
        sorted_params = sorted(data.items())
        query_string = '&'.join([f"{k}={v}" for k, v in sorted_params])
        
        # Generate HMAC signature
        signature = hmac.new(
            self.secret_key.encode('utf-8'),
            query_string.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
        
        return signature

class MaybankQRPayment(BankQRPayment):
    """Maybank QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.maybank2u.com.my"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate Maybank QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class CIMBQRPayment(BankQRPayment):
    """CIMB QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.cimb.com.my"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate CIMB QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class TouchNGoQRPayment(BankQRPayment):
    """Touch 'n Go QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.touchngo.com.my"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate Touch 'n Go QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class GrabPayQRPayment(BankQRPayment):
    """GrabPay QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.grab.com"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate GrabPay QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class MockQRPayment:
    """Mock QR Payment for testing (current implementation)"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Canteen Payment") -> Dict:
        """Generate mock QR payment"""
        return {
            'success': True,
            'qr_code': f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890",
            'qr_data': f"bank_qr://payment?amount={amount}&transaction_id={transaction_id}&merchant=MyMurid&account=1234567890",
            'payment_url': f"https://mock-payment.com/pay/{transaction_id}",
            'expires_at': (datetime.now(timezone(timedelta(hours=8))) + timedelta(minutes=15)).isoformat(),
            'reference_id': f"MOCK_{transaction_id}"
        }
    
    def check_payment_status(self, transaction_id: str) -> Dict:
        """Check mock payment status (simulates completion after 30 seconds)"""
        # Simulate payment completion after 30 seconds
        return {
            'success': True,
            'status': 'completed',
            'amount': '10.00',
            'paid_at': datetime.now(timezone(timedelta(hours=8))).isoformat(),
            'reference_id': f"MOCK_{transaction_id}"
        }

def get_payment_provider(provider_name: str, config: Dict) -> BankQRPayment:
    """Get payment provider instance"""
    
    providers = {
        'maybank': MaybankQRPayment,
        'cimb': CIMBQRPayment,
        'touchngo': TouchNGoQRPayment,
        'grabpay': GrabPayQRPayment,
        'mock': MockQRPayment
    }
    
    provider_class = providers.get(provider_name.lower(), MockQRPayment)
    return provider_class(config)

# Configuration for different providers
PAYMENT_CONFIGS = {
    'maybank': {
        'base_url': 'https://api.maybank2u.com.my',
        'merchant_id': 'YOUR_MAYBANK_MERCHANT_ID',
        'api_key': 'YOUR_MAYBANK_API_KEY',
        'secret_key': 'YOUR_MAYBANK_SECRET_KEY',
        'callback_url': 'https://yourdomain.com/api/payment/callback'
    },
    'cimb': {
        'base_url': 'https://api.cimb.com.my',
        'merchant_id': 'YOUR_CIMB_MERCHANT_ID',
        'api_key': 'YOUR_CIMB_API_KEY',
        'secret_key': 'YOUR_CIMB_SECRET_KEY',
        'callback_url': 'https://yourdomain.com/api/payment/callback'
    },
    'touchngo': {
        'base_url': 'https://api.touchngo.com.my',
        'merchant_id': 'YOUR_TNG_MERCHANT_ID',
        'api_key': 'YOUR_TNG_API_KEY',
        'secret_key': 'YOUR_TNG_SECRET_KEY',
        'callback_url': 'https://yourdomain.com/api/payment/callback'
    },
    'grabpay': {
        'base_url': 'https://api.grab.com',
        'merchant_id': 'YOUR_GRAB_MERCHANT_ID',
        'api_key': 'YOUR_GRAB_API_KEY',
        'secret_key': 'YOUR_GRAB_SECRET_KEY',
        'callback_url': 'https://yourdomain.com/api/payment/callback'
    },
    'mock': {
        'base_url': 'https://mock-payment.com',
        'merchant_id': 'MOCK_MERCHANT',
        'api_key': 'MOCK_API_KEY',
        'secret_key': 'MOCK_SECRET_KEY',
        'callback_url': 'https://yourdomain.com/api/payment/callback'
    }
}

# Example usage
if __name__ == "__main__":
    # Test with mock provider
    provider = get_payment_provider('mock', PAYMENT_CONFIGS['mock'])
    
    # Generate QR payment
    result = provider.generate_qr_payment(10.00, "TXN123456", "Test Payment")
    print("QR Payment Result:", json.dumps(result, indent=2))
    
    # Check payment status
    status = provider.check_payment_status("TXN123456")
    print("Payment Status:", json.dumps(status, indent=2))
