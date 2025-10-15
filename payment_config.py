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
                'callback_url': os.environ.get('PAYMENT_CALLBACK_URL', 'https://yourdomain.com/api/payment/callback')
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
