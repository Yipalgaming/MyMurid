#!/usr/bin/env python3
"""
Payment Configuration for MyMurid
"""

import os
from typing import Dict, Optional

class PaymentConfig:
    """Payment configuration management"""
    
    def __init__(self):
        self.provider = os.environ.get('PAYMENT_PROVIDER', 'mock')
        self.configs = self._load_configs()
    
    def _load_configs(self) -> Dict:
        """Load payment provider configurations"""
        return {
            'maybank': {
                'base_url': os.environ.get('MAYBANK_BASE_URL', 'https://api.maybank2u.com.my'),
                'merchant_id': os.environ.get('MAYBANK_MERCHANT_ID'),
                'api_key': os.environ.get('MAYBANK_API_KEY'),
                'secret_key': os.environ.get('MAYBANK_SECRET_KEY'),
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
            },
            'cimb': {
                'base_url': os.environ.get('CIMB_BASE_URL', 'https://api.cimb.com.my'),
                'merchant_id': os.environ.get('CIMB_MERCHANT_ID'),
                'api_key': os.environ.get('CIMB_API_KEY'),
                'secret_key': os.environ.get('CIMB_SECRET_KEY'),
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
            },
            'touchngo': {
                'base_url': os.environ.get('TNG_BASE_URL', 'https://api.touchngo.com.my'),
                'merchant_id': os.environ.get('TNG_MERCHANT_ID'),
                'api_key': os.environ.get('TNG_API_KEY'),
                'secret_key': os.environ.get('TNG_SECRET_KEY'),
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
            },
            'grabpay': {
                'base_url': os.environ.get('GRAB_BASE_URL', 'https://api.grab.com'),
                'merchant_id': os.environ.get('GRAB_MERCHANT_ID'),
                'api_key': os.environ.get('GRAB_API_KEY'),
                'secret_key': os.environ.get('GRAB_SECRET_KEY'),
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
            },
            'mock': {
                'base_url': 'https://mock-payment.com',
                'merchant_id': 'MOCK_MERCHANT',
                'api_key': 'MOCK_API_KEY',
                'secret_key': 'MOCK_SECRET_KEY',
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback'),
                # DuitNow QR Code (if canteen has existing DuitNow QR)
                'duitnow_qr_code': os.environ.get('DUITNOW_QR_CODE', ''),  # Full DuitNow QR code string
                # Single Canteen Bank Account Configuration
                # If CANTEEN_BANK_ACCOUNT is set, use single account. Otherwise, use multiple accounts.
                'canteen_bank_name': os.environ.get('CANTEEN_BANK_NAME', os.environ.get('TEST_BANK_1_NAME', 'Maybank')),
                'canteen_bank_account': os.environ.get('CANTEEN_BANK_ACCOUNT', os.environ.get('TEST_BANK_1_ACCOUNT', '1234567890')),
                'canteen_account_name': os.environ.get('CANTEEN_ACCOUNT_NAME', os.environ.get('TEST_BANK_1_ACCOUNT_NAME', 'Canteen Account')),
                # Multiple test bank accounts (fallback if single account not set)
                'test_accounts': [
                    {
                        'bank': os.environ.get('TEST_BANK_1_NAME', 'Maybank'),
                        'account': os.environ.get('TEST_BANK_1_ACCOUNT', '1234567890'),
                        'name': os.environ.get('TEST_BANK_1_ACCOUNT_NAME', 'MyMurid Test Account 1')
                    },
                    {
                        'bank': os.environ.get('TEST_BANK_2_NAME', 'CIMB'),
                        'account': os.environ.get('TEST_BANK_2_ACCOUNT', '0987654321'),
                        'name': os.environ.get('TEST_BANK_2_ACCOUNT_NAME', 'MyMurid Test Account 2')
                    },
                    {
                        'bank': os.environ.get('TEST_BANK_3_NAME', 'Public Bank'),
                        'account': os.environ.get('TEST_BANK_3_ACCOUNT', '1122334455'),
                        'name': os.environ.get('TEST_BANK_3_ACCOUNT_NAME', 'MyMurid Test Account 3')
                    }
                ]
            }
        }
    
    def get_config(self, provider: Optional[str] = None) -> Dict:
        """Get configuration for specified provider or current provider"""
        provider = provider or self.provider
        return self.configs.get(provider, self.configs['mock'])
    
    def is_production(self) -> bool:
        """Check if using production payment provider"""
        return self.provider != 'mock'
    
    def get_available_providers(self) -> list:
        """Get list of available payment providers"""
        return list(self.configs.keys())

# Global payment config instance
payment_config = PaymentConfig()
