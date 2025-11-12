# Information Needed from Canteen

## Overview

To set up the QR payment system, you need to get payment information from the canteen. There are **two options** depending on what the canteen has:

---

## Option 1: If Canteen Has DuitNow QR Code (Recommended)

### What to Ask For:

1. **DuitNow QR Code** (Physical QR code or image)
   - Ask the canteen for their DuitNow QR code
   - This can be:
     - A printed QR code poster/sticker
     - A digital QR code image
     - QR code from their payment terminal

2. **How to Get the QR Code String:**
   - Scan the QR code with any QR scanner app on your phone
   - Copy the text/data that appears (it will be a long string)
   - This is what you need to configure

### Example of What You'll Get:
```
00020101021226610012com.duitnow.mobile01021226610012com.duitnow.mobile5204000053037025802MY6009KUALALUMPUR61051234562070703***6304ABCD
```

### Configuration:
Add to your `.env` file:
```env
PAYMENT_PROVIDER=mock
DUITNOW_QR_CODE=00020101021226610012com.duitnow...your_full_qr_code_string_here
CANTEEN_ACCOUNT_NAME=School Canteen Account
```

---

## Option 2: If Canteen Has Maybank Account (No DuitNow QR)

### What to Ask For:

1. **Bank Name**
   - Example: `Maybank`

2. **Bank Account Number**
   - Example: `5678123456`
   - Make sure to get the full account number

3. **Account Name** (as it appears on the account)
   - Example: `School Canteen Account` or `SMK SEKSYEN 3 KANTIN`

### Configuration:
Add to your `.env` file:
```env
PAYMENT_PROVIDER=mock
CANTEEN_BANK_NAME=Maybank
CANTEEN_BANK_ACCOUNT=5678123456
CANTEEN_ACCOUNT_NAME=School Canteen Account
```

---

## Quick Checklist

### For DuitNow QR:
- [ ] Get DuitNow QR code from canteen
- [ ] Scan QR code with QR scanner app
- [ ] Copy the QR code string
- [ ] Add to `.env` file as `DUITNOW_QR_CODE`

### For Bank Account:
- [ ] Get bank name (e.g., Maybank)
- [ ] Get bank account number
- [ ] Get account name
- [ ] Add to `.env` file

---

## What to Say to the Canteen

**If asking for DuitNow QR:**
> "Hi, I need your DuitNow QR code for the school payment system. Do you have a DuitNow QR code that parents can scan to pay?"

**If asking for bank account:**
> "Hi, I need your bank account details (bank name and account number) for the school payment system. Parents will transfer money to this account for student top-ups."

---

## Important Notes

⚠️ **Security:**
- Keep bank account numbers secure
- Never commit `.env` file to version control
- Only share account details with authorized personnel

⚠️ **Verification:**
- Always verify the account number with the canteen
- Double-check the account name matches
- Test with a small amount first

⚠️ **DuitNow vs Bank Account:**
- **DuitNow QR** is better - works with all banks and e-wallets
- **Bank Account** is simpler - just need account number
- Choose based on what the canteen has

---

## After Getting the Information

1. Add the information to your `.env` file
2. Restart the Flask application
3. Test the QR code generation
4. Verify the account number/QR code is correct
5. Test with a small payment amount

---

**That's it!** Once you have either the DuitNow QR code or bank account details, you can configure the payment system.

