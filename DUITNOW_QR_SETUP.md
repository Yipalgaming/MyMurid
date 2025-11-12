# DuitNow QR Code Setup Guide

## Overview

If the canteen already has a **DuitNow QR code**, you can use it directly in the system instead of generating QR codes with bank account numbers.

## What is DuitNow?

**DuitNow** is Malaysia's national QR payment standard that works with all major Malaysian banks and e-wallets:
- ✅ Maybank
- ✅ CIMB
- ✅ Public Bank
- ✅ Touch 'n Go
- ✅ GrabPay
- ✅ And many more...

## What You Need

If the canteen has a DuitNow QR code, you need:

1. **DuitNow QR Code String** - The actual QR code data/text
   - This is usually a long string that starts with something like `000201` or contains merchant/bank information
   - You can get this by scanning the QR code with a QR scanner app

2. **How to Get the QR Code String:**
   - Scan the canteen's DuitNow QR code with any QR scanner app
   - Copy the text/data that appears
   - This is your `DUITNOW_QR_CODE`

## Configuration

Add this to your `.env` file:

```env
# Payment Provider (use 'mock' for DuitNow QR)
PAYMENT_PROVIDER=mock

# DuitNow QR Code (if canteen has existing DuitNow QR)
DUITNOW_QR_CODE=00020101021226610012com.duitnow...your_full_qr_code_string_here

# Optional: Canteen Account Name
CANTEEN_ACCOUNT_NAME=School Canteen Account
```

### Example:

```env
PAYMENT_PROVIDER=mock
DUITNOW_QR_CODE=00020101021226610012com.duitnow.mobile01021226610012com.duitnow.mobile5204000053037025802MY6009KUALALUMPUR61051234562070703***6304ABCD
CANTEEN_ACCOUNT_NAME=School Canteen Account
```

## How It Works

1. **Parent requests top-up** → System generates QR code using the canteen's DuitNow QR
2. **Parent scans QR code** → Opens their bank/e-wallet app (Maybank, CIMB, TNG, etc.)
3. **Parent pays** → Money goes directly to canteen's account via DuitNow
4. **Admin verifies** → Checks bank statement/notification
5. **Admin approves** → Via `/admin/payments` page
6. **Balance updated** → Student balance updates automatically

## Benefits of Using DuitNow QR

✅ **Universal** - Works with all major Malaysian banks and e-wallets  
✅ **No Account Number Needed** - QR code contains all payment info  
✅ **Easy for Parents** - Just scan and pay with their preferred app  
✅ **Secure** - DuitNow is Malaysia's national standard  
✅ **Fast** - Direct payment processing  

## Important Notes

⚠️ **QR Code Format:**
- DuitNow QR codes are usually long strings (100+ characters)
- They may include merchant ID, bank info, and other data
- The exact format may vary - use the full string from scanning

⚠️ **Amount Handling:**
- Some DuitNow QR codes support dynamic amounts
- The system will append amount and transaction reference to the QR code
- If the QR code doesn't support dynamic amounts, parents will need to enter the amount manually in their app

⚠️ **Transaction Reference:**
- The system includes a transaction reference in the QR code
- Parents should include this reference when making payment
- Admin can verify payments using this reference

## Testing

1. Add `DUITNOW_QR_CODE` to `.env`
2. Restart Flask application
3. Test QR code generation:
   - Go to Parent Dashboard → Select Child → Top Up
   - Enter amount → Generate QR Code
   - QR code should show the DuitNow QR
4. Test scanning:
   - Scan QR code with bank/e-wallet app
   - Verify it opens the payment screen
   - Check if amount is pre-filled (depends on QR code format)

## Troubleshooting

**QR code doesn't scan:**
- Verify the QR code string is complete
- Make sure there are no extra spaces or line breaks
- Try scanning the original QR code again to get the exact string

**Amount not showing:**
- Some DuitNow QR codes don't support dynamic amounts
- Parents will need to enter amount manually in their app
- This is normal for static DuitNow QR codes

**Payment not recognized:**
- Ensure parents include the transaction reference when paying
- Admin should verify payment using the transaction ID
- Check bank statement for incoming payments

---

**That's it!** Once configured, the system will use the canteen's DuitNow QR code for all payments.

