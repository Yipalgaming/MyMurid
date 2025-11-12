# Maybank QR Payment Integration - What You Need

## Overview
To integrate Maybank QR payments into your MyMurid system, you'll need to apply for Maybank's merchant services and obtain API credentials.

## What You Need from Maybank

### 1. **Merchant Account Registration**
You need to apply for:
- **Maybank Merchant Account** - Register as a merchant with Maybank
- **Maybank QR Payment Solution** - Specifically for QR code payments

**Contact Points:**
- **Maybank Merchant Services**: Visit your nearest Maybank branch
- **Online Application**: https://www.maybank.com/en/business/merchant-solutions/
- **Phone**: 1-300-88-6688 (Maybank Business Banking)
- **Email**: merchant.services@maybank.com.my

### 2. **Required Documentation**
When applying, you'll typically need:
- Business registration documents (SSM/Company registration)
- Business bank account details
- Company identification documents
- Business address and contact information
- Tax ID (if applicable)
- Business description and nature of business

### 3. **API Credentials**
Once approved, Maybank will provide you with:

#### **Merchant ID**
- Unique identifier for your merchant account
- Format: Usually alphanumeric (e.g., `MERCH123456`)

#### **API Key**
- Used for authentication when making API calls
- Must be kept secure and never exposed publicly

#### **Secret Key**
- Used for generating HMAC signatures
- Critical for security - never share or commit to version control

#### **API Base URL**
- Sandbox/Testing: `https://sandbox-api.maybank2u.com.my` (if available)
- Production: `https://api.maybank2u.com.my`

#### **API Documentation**
- Technical documentation for integration
- API endpoint specifications
- Request/response formats
- Error codes and handling

### 4. **Maybank QR Payment Solutions**

Maybank offers different QR payment solutions:

#### **a) DuitNow QR (Malaysia's National QR Standard)**
- Most common QR payment method in Malaysia
- Works with all major Malaysian banks
- Standardized QR code format

#### **b) Maybank QR Pay**
- Maybank's proprietary QR payment solution
- Integrated with Maybank2u mobile app

**Recommended:** DuitNow QR for broader customer acceptance

### 5. **Technical Requirements**

#### **SSL Certificate**
- Your website must have a valid SSL certificate (HTTPS)
- Required for secure API communication
- Required for payment callback URLs

#### **Callback URL**
- Public URL where Maybank will send payment notifications
- Must be accessible from the internet
- Example: `https://yourdomain.com/api/payment/callback`

#### **Webhook Endpoint**
- Your server endpoint to receive payment status updates
- Must handle POST requests from Maybank
- Must verify webhook signatures for security

### 6. **Maybank API Features**

You'll have access to:
- **QR Code Generation** - Generate QR codes for payments
- **Payment Status Check** - Query payment status
- **Transaction History** - View past transactions
- **Refund Processing** - Process refunds if needed
- **Settlement Reports** - View settlement information

### 7. **Costs & Fees**

Check with Maybank about:
- **Setup Fee** - One-time merchant account setup fee
- **Transaction Fees** - Per-transaction charges (usually 0.5% - 2%)
- **Monthly Fees** - Any monthly maintenance fees
- **Minimum Transaction Volume** - Some plans require minimum volume

### 8. **Application Process**

**Step 1: Initial Inquiry**
1. Contact Maybank Merchant Services
2. Express interest in QR payment integration
3. Request information about their API program

**Step 2: Application**
1. Complete merchant application form
2. Submit required documentation
3. Provide business details and use case

**Step 3: Approval & Onboarding**
1. Wait for approval (can take 1-4 weeks)
2. Receive merchant credentials
3. Access to sandbox/testing environment
4. Technical integration support

**Step 4: Production Setup**
1. Complete integration testing
2. Submit for production approval
3. Receive production credentials
4. Go live

### 9. **Alternative: Maybank Merchant Portal**

If full API access is not available, Maybank may offer:
- **Merchant Portal** - Web-based interface to generate QR codes
- **Manual QR Generation** - Generate QR codes through portal
- **Payment Reconciliation** - View payments through portal

### 10. **What to Ask Maybank**

When contacting Maybank, ask specifically:
1. "Do you offer QR payment API integration for merchants?"
2. "I need API credentials for DuitNow QR payment integration"
3. "What are the requirements for API access?"
4. "Is there a sandbox/test environment available?"
5. "What is the application process and timeline?"
6. "What are the fees and charges?"
7. "Do you provide technical integration support?"

### 11. **Configuration in Your System**

Once you have the credentials, add them to your `.env` file:

```env
# Set Maybank as payment provider
PAYMENT_PROVIDER=maybank

# Maybank API Credentials
MAYBANK_MERCHANT_ID=your_merchant_id_here
MAYBANK_API_KEY=your_api_key_here
MAYBANK_SECRET_KEY=your_secret_key_here
MAYBANK_BASE_URL=https://api.maybank2u.com.my

# Your callback URL (must be HTTPS)
PAYMENT_CALLBACK_URL=https://yourdomain.com/api/payment/callback
```

### 12. **Important Notes**

⚠️ **Security:**
- Never commit API credentials to version control
- Store credentials in environment variables only
- Use different credentials for testing and production
- Rotate credentials periodically

⚠️ **Testing:**
- Always test in sandbox/test environment first
- Test with small amounts before going live
- Verify webhook/callback handling works correctly

⚠️ **Compliance:**
- Ensure your payment processing complies with PCI DSS
- Follow Maybank's terms and conditions
- Implement proper error handling and logging

### 13. **Support Resources**

- **Maybank Merchant Services**: 1-300-88-6688
- **Maybank Business Banking**: https://www.maybank.com/en/business/
- **Maybank API Documentation**: (Provided after approval)
- **Technical Support**: (Contact provided during onboarding)

### 14. **Alternative Options**

If Maybank API is not available or too complex:

1. **Maybank Merchant Portal** - Manual QR generation
2. **DuitNow Cash Out** - Alternative payment method
3. **Payment Gateway Providers** - Third-party services like:
   - iPay88
   - SenangPay
   - MOLPay
   - Stripe (if available in Malaysia)

These providers often offer easier integration and support multiple payment methods.

---

## Quick Start Checklist

- [ ] Contact Maybank Merchant Services
- [ ] Complete merchant application
- [ ] Receive API credentials
- [ ] Get sandbox/test environment access
- [ ] Review API documentation
- [ ] Configure environment variables
- [ ] Test integration in sandbox
- [ ] Submit for production approval
- [ ] Configure production credentials
- [ ] Go live with real payments

---

**Note:** The actual API endpoints and authentication methods may vary based on Maybank's current implementation. Always refer to the official API documentation provided by Maybank after approval.

