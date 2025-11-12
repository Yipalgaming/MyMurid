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
                          description: str = "MyMurid Payment") -> Dict:
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
                          description: str = "MyMurid Payment") -> Dict:
        """Generate Maybank QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class CIMBQRPayment(BankQRPayment):
    """CIMB QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.cimb.com.my"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Payment") -> Dict:
        """Generate CIMB QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class TouchNGoQRPayment(BankQRPayment):
    """Touch 'n Go QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.touchngo.com.my"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Payment") -> Dict:
        """Generate Touch 'n Go QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class GrabPayQRPayment(BankQRPayment):
    """GrabPay QR Payment Integration"""
    
    def __init__(self, config: Dict):
        super().__init__(config)
        self.base_url = "https://api.grab.com"
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Payment") -> Dict:
        """Generate GrabPay QR payment"""
        return super().generate_qr_payment(amount, transaction_id, description)

class MockQRPayment:
    """Mock QR Payment for testing with manual bank account transfers"""
    
    def __init__(self, config: Dict = None):
        self.config = config or {}
        # Check if single canteen account is configured
        self.canteen_account = None
        if config and config.get('canteen_bank_account'):
            self.canteen_account = {
                'bank': config.get('canteen_bank_name', 'Canteen Bank'),
                'account': config.get('canteen_bank_account'),
                'name': config.get('canteen_account_name', 'Canteen Account')
            }
        
        # Get test bank accounts from config (fallback if single account not set)
        self.test_accounts = config.get('test_accounts', [
            {'bank': 'Maybank', 'account': '1234567890', 'name': 'MyMurid Test Account 1'},
            {'bank': 'CIMB', 'account': '0987654321', 'name': 'MyMurid Test Account 2'},
            {'bank': 'Public Bank', 'account': '1122334455', 'name': 'MyMurid Test Account 3'}
        ])
        
    def generate_qr_payment(self, amount: float, transaction_id: str, 
                          description: str = "MyMurid Payment") -> Dict:
        """Generate mock QR payment with bank account number or DuitNow QR"""
        # Check if canteen has existing DuitNow QR code
        duitnow_qr = self.config.get('duitnow_qr_code', '')
        if duitnow_qr and duitnow_qr.strip():
            # Use existing DuitNow QR code exactly as provided
            # DuitNow QR codes are static and must be used as-is
            # Users will enter the amount manually in their payment app
            # DO NOT modify the QR code string - it breaks the EMV format
            
            return {
                'success': True,
                'qr_code': duitnow_qr.strip(),
                'qr_data': duitnow_qr.strip(),  # Use exact QR code as provided
                'payment_url': f"/admin/payments/{transaction_id}",
                'expires_at': (datetime.now(timezone(timedelta(hours=8))) + timedelta(minutes=15)).isoformat(),
                'reference_id': f"DUITNOW_{transaction_id[:8]}",
                'bank_account': None,  # DuitNow QR doesn't show account number
                'bank_name': 'DuitNow',
                'account_name': self.config.get('canteen_account_name', 'Canteen Account'),
                'is_duitnow': True
            }
        
        # Use single canteen account if configured, otherwise rotate between multiple accounts
        if self.canteen_account:
            selected_account = self.canteen_account
        else:
            # Use first account by default, or rotate based on transaction ID
            import hashlib
            account_index = int(hashlib.md5(transaction_id.encode()).hexdigest(), 16) % len(self.test_accounts)
            selected_account = self.test_accounts[account_index]
        
        # Generate QR data with bank account details
        qr_data = f"PAYMENT|{selected_account['bank']}|{selected_account['account']}|{amount:.2f}|{transaction_id}|MyMurid"
        
        return {
            'success': True,
            'qr_code': qr_data,
            'qr_data': qr_data,
            'payment_url': f"/admin/payments/{transaction_id}",
            'expires_at': (datetime.now(timezone(timedelta(hours=8))) + timedelta(minutes=15)).isoformat(),
            'reference_id': f"TEST_{transaction_id}",
            'bank_account': selected_account['account'],
            'bank_name': selected_account['bank'],
            'account_name': selected_account['name'],
            'is_duitnow': False
        }
    
    def check_payment_status(self, transaction_id: str) -> Dict:
        """Check mock payment status - returns pending unless manually approved"""
        # This will be checked against database - return pending for manual approval
        return {
            'success': True,
            'status': 'pending',  # Admin must manually approve
            'amount': None,
            'paid_at': None,
            'reference_id': f"TEST_{transaction_id}"
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
