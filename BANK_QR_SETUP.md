# Bank QR Payment Integration Setup

## Overview
The MyMurid system now supports real bank QR payments through multiple Malaysian payment providers.

## Supported Providers
- **Maybank** - Maybank2u QR
- **CIMB** - CIMB QR
- **Touch 'n Go** - TNG QR
- **GrabPay** - GrabPay QR
- **Mock** - For testing (current default)

## Setup Instructions

### 1. Choose Your Payment Provider
Edit your `.env` file and set the provider:
```env
PAYMENT_PROVIDER=maybank  # or cimb, touchngo, grabpay, mock
```

### 2. Get API Credentials
Contact your chosen bank/payment provider to get:
- Merchant ID
- API Key
- Secret Key
- API Documentation

### 3. Configure Environment Variables
Add these to your `.env` file (example for Maybank):
```env
# Maybank Configuration
MAYBANK_MERCHANT_ID=your_merchant_id
MAYBANK_API_KEY=your_api_key
MAYBANK_SECRET_KEY=your_secret_key
MAYBANK_BASE_URL=https://api.maybank2u.com.my

# Payment Callback URL (where bank will notify payment status)
PAYMENT_CALLBACK_URL=https://yourdomain.com/api/payment/callback
```

### 4. Test the Integration
1. Start with `PAYMENT_PROVIDER=mock` to test the flow
2. Switch to your real provider once everything works
3. Test with small amounts first

## How It Works

### QR Generation
1. Parent initiates payment for child
2. System calls bank API to generate QR code
3. QR code is displayed to parent
4. Parent scans QR with bank app

### Payment Status Check
1. System polls bank API for payment status
2. When payment is confirmed, child's balance is updated
3. Payment record is marked as completed

### Security Features
- HMAC signature verification
- Transaction ID validation
- Secure API key handling
- Callback URL verification

## API Endpoints

### Generate QR Payment
```
POST /parent/payment/<child_id>
```
- Creates payment record
- Generates QR code via bank API
- Returns QR data for display

### Check Payment Status
```
GET /api/payment/status/<transaction_id>
```
- Checks payment status with bank
- Updates local payment record
- Returns current status

## Error Handling
- Falls back to mock provider if real provider fails
- Logs all API errors for debugging
- Graceful degradation for network issues

## Testing
Use the mock provider for development:
```env
PAYMENT_PROVIDER=mock
```
This simulates payment completion after 30 seconds.

## Production Deployment
1. Get real API credentials from your bank
2. Update environment variables
3. Set up SSL certificate for callback URL
4. Test with small amounts
5. Monitor logs for any issues

## Support
- Check bank's API documentation
- Monitor application logs
- Test with mock provider first
- Contact bank support for API issues
