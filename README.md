# Telebirr Receipt Parser

A Python library for **fetching, parsing, and verifying Ethiopian Telebirr transaction receipts** from the official Ethio Telecom transaction information service.

The library is designed to make it easy to retrieve a Telebirr receipt using its receipt number, extract transaction information, check payment status, verify payer and recipient details, verify payment amounts, and serialize receipt data to dictionaries or JSON.

---

## Features

- Fetch Telebirr receipts directly using a receipt number
- Parse Telebirr receipt HTML
- Support Amharic/English mixed receipt labels
- Extract payer information
- Extract recipient information
- Extract transaction status
- Extract payment date
- Extract settled amount
- Extract total paid amount
- Extract service fees
- Extract service fee VAT
- Extract stamp duty
- Extract discount amount
- Extract payment mode
- Extract payment reason
- Extract payment channel
- Extract customer notes
- Check whether a receipt exists
- Check whether a transaction is completed
- Verify payer name and Telebirr number
- Verify recipient name and Telebirr number
- Support masked Telebirr numbers
- Verify payment amounts
- Verify transaction status
- Perform complete payment verification
- Return receipt data as a Python dictionary
- Return receipt data as JSON
- Automatic HTTP retries for temporary server errors
- Custom exceptions for fetching, parsing, and receipt errors

---

## Installation

Install the package from PyPI:

```bash
pip install telebirr-receipt
```

You can also install it using:

```bash
python -m pip install telebirr-receipt
```

After installation, import the package:

```python
from telebirr_receipt import TelebirrReceipt
```

---

## Requirements

The package requires:

- Python 3.9+
- `requests`
- `beautifulsoup4`

These dependencies are installed automatically when you install the package with pip.

---

# Quick Start

The simplest way to use the library is to create a `TelebirrReceipt` instance with a receipt number and call `load()`.

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

receipt.load()

print(receipt.receipt_no)
print(receipt.payer_name)
print(receipt.credited_party_name)
print(receipt.total_paid_amount)
print(receipt.transaction_status)
```

Example output:

```text
FT123456789
John Doe
Jane Doe
100.0
Completed
```

Replace `YOUR_RECEIPT_NUMBER` with the actual Telebirr receipt number.

---

# How It Works

The library performs the following process:

```text
Receipt Number
      │
      ▼
Telebirr Transaction Service
      │
      ▼
Receipt HTML
      │
      ▼
HTML Parser
      │
      ▼
TelebirrReceipt object
      │
      ├── Payer information
      ├── Recipient information
      ├── Transaction information
      ├── Amount information
      └── Payment information
```

The library requests the receipt page from the Telebirr transaction information service and parses the returned HTML using BeautifulSoup.

The receipt URL is generated from the receipt number.

---

# Basic Usage

## Create a Receipt Object

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")
```

At this point, the receipt has not necessarily been fetched yet.

The receipt is fetched when you call methods such as:

```python
receipt.load()
```

or methods that require receipt data.

---

# Load a Receipt

Use `load()` to fetch and parse the receipt.

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

receipt.load()

print(receipt.receipt_no)
```

`load()`:

1. Fetches the receipt from Telebirr
2. Parses the HTML
3. Extracts the transaction information
4. Populates the `TelebirrReceipt` object
5. Returns the same receipt object

You can therefore also write:

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER").load()
```

---

# Check Whether a Receipt Exists

Use `exists()` when you only need to know whether a receipt can be successfully retrieved.

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

if receipt.exists():
    print("Receipt exists")
else:
    print("Receipt does not exist")
```

`exists()` returns:

```text
True
```

or:

```text
False
```

The method catches Telebirr-related errors and returns `False` when the receipt cannot be successfully loaded.

---

# Check Transaction Status

Use `is_completed()` to determine whether the transaction status is `Completed`.

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

if receipt.is_completed():
    print("Payment completed")
else:
    print("Payment is not completed")
```

The comparison is case-insensitive.

For example:

```text
Completed
completed
COMPLETED
```

are treated as the same status.

---

# Get Payment Amount

Use `get_amount()` to get the total paid amount as a numeric value.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

amount = receipt.get_amount()

print(amount)
```

Example:

```text
100.0
```

The parser converts amount strings such as:

```text
50 Birr
0.87 Birr
1,234.56
```

into numeric floating-point values.

---

# Get Settled Amount

Use:

```python
settled_amount = receipt.get_settled_amount()

print(settled_amount)
```

Example:

```text
100.0
```

The settled amount is separate from the total paid amount.

---

# Get Payer Information

## Payer Name

```python
name = receipt.get_payer_name()

print(name)
```

You can also access:

```python
receipt.payer_name
```

---

## Payer Telebirr Number

```python
number = receipt.get_payer_number()

print(number)
```

You can also access:

```python
receipt.payer_telebirr_no
```

---

# Get Recipient Information

## Recipient Name

```python
name = receipt.get_recipient_name()

print(name)
```

You can also access:

```python
receipt.credited_party_name
```

---

## Recipient Telebirr Number

```python
number = receipt.get_recipient_number()

print(number)
```

You can also access:

```python
receipt.credited_party_account_no
```

---

# Receipt Data

The `TelebirrReceipt` object contains the following fields.

## Receipt Information

```python
receipt.receipt_no
receipt.fetched_at
```

---

## Payer Information

```python
receipt.payer_name
receipt.payer_telebirr_no
receipt.payer_account_type
receipt.payer_tin_no
receipt.payer_vat_reg_no
receipt.payer_vat_reg_date
```

---

## Recipient Information

```python
receipt.credited_party_name
receipt.credited_party_account_no
```

---

## Transaction Information

```python
receipt.transaction_status
receipt.payment_date
```

---

## Amount Information

Raw amount values:

```python
receipt.settled_amount_raw
receipt.stamp_duty_raw
receipt.discount_amount_raw
receipt.service_fee_raw
receipt.service_fee_vat_raw
receipt.total_paid_amount_raw
```

Parsed numeric values:

```python
receipt.settled_amount
receipt.stamp_duty
receipt.discount_amount
receipt.service_fee
receipt.service_fee_vat
receipt.total_paid_amount
```

---

## Payment Information

```python
receipt.total_amount_in_words
receipt.payment_mode
receipt.payment_reason
receipt.payment_channel
receipt.customer_note
```

---

# Convert Receipt to Dictionary

Use `to_dict()` to convert the receipt into a Python dictionary.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

receipt.load()

data = receipt.to_dict()

print(data)
```

Example structure:

```python
{
    "receipt_no": "...",
    "payer_name": "...",
    "payer_telebirr_no": "...",
    "payer_account_type": "...",
    "credited_party_name": "...",
    "credited_party_account_no": "...",
    "transaction_status": "Completed",
    "payment_date": "...",
    "settled_amount": 100.0,
    "total_paid_amount": 100.0,
    "payment_mode": "...",
    "payment_reason": "...",
    "payment_channel": "...",
    "customer_note": "...",
    "raw_pairs": {...},
    "fetched_at": "..."
}
```

The exact values depend on the receipt.

---

# Convert Receipt to JSON

Use `to_json()` when you need a JSON string.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

receipt.load()

json_data = receipt.to_json()

print(json_data)
```

You can also specify the indentation:

```python
json_data = receipt.to_json(indent=4)
```

---

# Verify Recipient

You can verify that the receipt belongs to a specific recipient.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

result = receipt.check_recipient(
    name="Jane Doe",
    number="251912345678"
)

print(result)
```

The method returns:

```text
True
```

if both the recipient name and number match.

Otherwise it returns:

```text
False
```

---

## Case-Insensitive Recipient Verification

By default, recipient name comparison ignores case.

```python
receipt.check_recipient(
    name="jane doe",
    number="251912345678"
)
```

is equivalent to:

```python
receipt.check_recipient(
    name="Jane Doe",
    number="251912345678"
)
```

You can disable case-insensitive matching:

```python
receipt.check_recipient(
    name="Jane Doe",
    number="251912345678",
    ignore_case=False
)
```

---

# Verify Payer

You can also verify the payer.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

result = receipt.check_payer(
    name="John Doe",
    number="251912345678"
)

print(result)
```

The method verifies both:

- Payer name
- Payer Telebirr number

---

# Masked Telebirr Numbers

Telebirr receipts may contain masked numbers.

For example:

```text
2519****6652
```

The library supports comparison between masked and full numbers.

For example:

```python
receipt.check_recipient(
    name="Jane Doe",
    number="251912346652"
)
```

can match a receipt containing:

```text
2519****6652
```

The comparison checks the visible prefix and suffix of the masked number.

---

# Complete Payment Verification

For payment-processing applications, you can perform multiple verification checks at once using `verify_payment()`.

```python
receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

result = receipt.verify_payment(
    expected_recipient_name="Jane Doe",
    expected_recipient_number="251912345678",
    expected_amount=100.00,
)

print(result)
```

The method can verify:

- Transaction status
- Payment amount
- Payer name
- Payer number
- Recipient name
- Recipient number

All checks are optional.

---

# Verify Amount

You can verify that the payment amount matches an expected amount.

```python
result = receipt.verify_payment(
    expected_amount=100.00
)

print(result)
```

The result contains:

```python
result["valid"]
```

and:

```python
result["checks"]["amount"]
```

---

# Amount Tolerance

You can specify an amount tolerance.

```python
result = receipt.verify_payment(
    expected_amount=100.00,
    amount_tolerance=0.01
)
```

This allows a small difference between the expected and actual amount.

For example, with:

```python
amount_tolerance=0.01
```

an actual amount of:

```text
100.005
```

can be accepted depending on the comparison result.

---

# Verify Transaction Status

By default, `verify_payment()` expects the transaction status to be:

```text
Completed
```

Example:

```python
result = receipt.verify_payment(
    expected_status="Completed"
)
```

You can specify another expected status:

```python
result = receipt.verify_payment(
    expected_status="Pending"
)
```

Status comparison is case-insensitive.

---

# Verify Payer

```python
result = receipt.verify_payment(
    expected_payer_name="John Doe",
    expected_payer_number="251912345678"
)
```

---

# Verify Recipient

```python
result = receipt.verify_payment(
    expected_recipient_name="Jane Doe",
    expected_recipient_number="251987654321"
)
```

---

# Verify Everything

You can combine all available checks:

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

result = receipt.verify_payment(
    expected_recipient_name="Jane Doe",
    expected_recipient_number="251987654321",
    expected_payer_name="John Doe",
    expected_payer_number="251912345678",
    expected_amount=100.00,
    expected_status="Completed",
    amount_tolerance=0.0,
)

print(result)
```

The returned dictionary contains:

```python
{
    "valid": True,
    "receipt_no": "...",
    "status": "Completed",
    "amount": 100.0,
    "recipient": {
        "name": "...",
        "number": "..."
    },
    "payer": {
        "name": "...",
        "number": "..."
    },
    "checks": {
        "status": True,
        "amount": True,
        "payer_name": True,
        "payer_number": True,
        "recipient_name": True,
        "recipient_number": True
    },
    "errors": {}
}
```

If one or more checks fail, `valid` becomes:

```python
False
```

and the `errors` dictionary contains information about the failed checks.

---

# Example: Payment Verification in an Application

A common use case is verifying a payment before giving a user access to a product or service.

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

result = receipt.verify_payment(
    expected_recipient_name="My Business",
    expected_recipient_number="2519XXXXXXXX",
    expected_amount=500.00,
)

if result["valid"]:
    print("Payment verified")
else:
    print("Payment verification failed")
    print(result["errors"])
```

This allows your application to check the receipt information before processing the transaction.

---

# Error Handling

The package provides custom exceptions for different failure cases.

Import them with:

```python
from telebirr_receipt import (
    TelebirrReceipt,
    TelebirrError,
    TelebirrFetchError,
    TelebirrParseError,
    ReceiptNotFoundError,
    PaymentVerificationError,
)
```

---

## TelebirrError

`TelebirrError` is the base exception for errors raised by the package.

You can catch all package-specific errors with:

```python
try:
    receipt.load()
except TelebirrError as error:
    print(error)
```

---

## TelebirrFetchError

Raised when the receipt cannot be fetched successfully.

```python
try:
    receipt.load()
except TelebirrFetchError as error:
    print("Failed to fetch receipt:", error)
```

This can happen because of network problems or unexpected HTTP responses.

---

## ReceiptNotFoundError

Raised when the receipt does not exist or the receipt page does not contain the required transaction information.

```python
try:
    receipt.load()
except ReceiptNotFoundError:
    print("Receipt not found")
```

---

## TelebirrParseError

Raised when the returned HTML cannot be parsed correctly.

```python
try:
    receipt.load()
except TelebirrParseError as error:
    print("Unable to parse receipt:", error)
```

---

## PaymentVerificationError

The package exposes `PaymentVerificationError` as a custom payment-verification exception type.

```python
from telebirr_receipt import PaymentVerificationError
```

---

# Recommended Error Handling

For a production application:

```python
from telebirr_receipt import (
    TelebirrReceipt,
    TelebirrError,
    ReceiptNotFoundError,
)

receipt = TelebirrReceipt("YOUR_RECEIPT_NUMBER")

try:
    receipt.load()

    result = receipt.verify_payment(
        expected_amount=100.00,
        expected_status="Completed",
    )

    if result["valid"]:
        print("Payment verified")
    else:
        print("Payment verification failed")
        print(result["errors"])

except ReceiptNotFoundError:
    print("Receipt does not exist")

except TelebirrError as error:
    print("Telebirr error:", error)
```

---

# HTTP Requests and Retries

The library uses `requests` to communicate with the Telebirr transaction information service.

Temporary HTTP errors are automatically retried.

The retry configuration includes:

```text
429
500
502
503
504
```

The library uses multiple retry attempts with exponential-style backoff.

TLS certificate verification is enabled for requests.

---

# Raw Receipt Data

The parser keeps the extracted label/value pairs in:

```python
receipt.raw_pairs
```

Example:

```python
receipt.load()

print(receipt.raw_pairs)
```

This can be useful when you want to inspect the values extracted directly from the receipt.

---

# Full Example

```python
from telebirr_receipt import (
    TelebirrReceipt,
    TelebirrError,
    ReceiptNotFoundError,
)

receipt_number = "YOUR_RECEIPT_NUMBER"

receipt = TelebirrReceipt(receipt_number)

try:
    receipt.load()

    print("Receipt:", receipt.receipt_no)
    print("Payer:", receipt.get_payer_name())
    print("Payer Number:", receipt.get_payer_number())

    print("Recipient:", receipt.get_recipient_name())
    print("Recipient Number:", receipt.get_recipient_number())

    print("Status:", receipt.transaction_status)
    print("Payment Date:", receipt.payment_date)

    print("Settled Amount:", receipt.get_settled_amount())
    print("Total Paid:", receipt.get_amount())

    if receipt.is_completed():
        print("Transaction completed")

    result = receipt.verify_payment(
        expected_recipient_name="Jane Doe",
        expected_recipient_number="251987654321",
        expected_amount=100.00,
        expected_status="Completed",
    )

    if result["valid"]:
        print("Payment verified successfully")
    else:
        print("Payment verification failed")
        print(result["errors"])

except ReceiptNotFoundError:
    print("Receipt was not found")

except TelebirrError as error:
    print("Telebirr error:", error)
```

---

# API Reference

## `TelebirrReceipt`

The main class provided by the package.

```python
TelebirrReceipt(receipt_no=None)
```

### Methods

| Method                   | Description                                |
| ------------------------ | ------------------------------------------ |
| `fetch()`                | Fetch the raw receipt HTML                 |
| `parse(html)`            | Parse receipt HTML                         |
| `load()`                 | Fetch and parse the receipt                |
| `exists()`               | Check whether the receipt exists           |
| `is_completed()`         | Check whether the transaction is completed |
| `get_amount()`           | Get the total paid amount                  |
| `get_settled_amount()`   | Get the settled amount                     |
| `get_payer_name()`       | Get payer name                             |
| `get_payer_number()`     | Get payer Telebirr number                  |
| `get_recipient_name()`   | Get recipient name                         |
| `get_recipient_number()` | Get recipient account number               |
| `check_recipient()`      | Verify recipient name and number           |
| `check_payer()`          | Verify payer name and number               |
| `verify_payment()`       | Perform complete payment verification      |
| `to_dict()`              | Convert receipt to dictionary              |
| `to_json()`              | Convert receipt to JSON                    |

---

# Data Model

The main receipt object contains information including:

### Payer

```text
payer_name
payer_telebirr_no
payer_account_type
payer_tin_no
payer_vat_reg_no
payer_vat_reg_date
```

### Recipient

```text
credited_party_name
credited_party_account_no
```

### Transaction

```text
receipt_no
transaction_status
payment_date
```

### Amounts

```text
settled_amount
stamp_duty
discount_amount
service_fee
service_fee_vat
total_paid_amount
```

### Payment

```text
total_amount_in_words
payment_mode
payment_reason
payment_channel
customer_note
```

### Additional Data

```text
raw_pairs
fetched_at
```

---

# Important Note

This package depends on the HTML structure of the Telebirr transaction information service.

If the structure of the official receipt page changes, the parser may require an update.

The library does not control the Telebirr transaction service or its availability.

---

# Responsible Use

This package is intended for legitimate software development and payment verification use cases.

Do not use it to:

- Misrepresent payments
- Fraudulently verify transactions
- Access information you are not authorized to access
- Abuse the Telebirr service
- Circumvent security or access controls

Make sure your application's use of receipt information complies with applicable laws, regulations, and the policies of the relevant service providers.

---

# Django / Django REST Framework

The package can also be used inside Django or Django REST Framework applications.

For example:

```python
from telebirr_receipt import TelebirrReceipt

receipt = TelebirrReceipt(receipt_number)

result = receipt.verify_payment(
    expected_recipient_name="My Business",
    expected_recipient_number="2519XXXXXXXX",
    expected_amount=100.00,
)

if result["valid"]:
    # Process verified payment
    pass
```

This allows the receipt parser to remain a reusable Python library while your Django application handles:

- Authentication
- Database operations
- API endpoints
- Business logic
- User accounts
- Payment records

---

# Example REST API Integration

A Django REST Framework view could use the package like this:

```python
from rest_framework.response import Response
from rest_framework.views import APIView

from telebirr_receipt import TelebirrReceipt


class VerifyPaymentView(APIView):

    def post(self, request):

        receipt_number = request.data.get("receipt_number")

        receipt = TelebirrReceipt(receipt_number)

        result = receipt.verify_payment(
            expected_amount=100.00,
            expected_status="Completed",
        )

        return Response(result)
```

The package itself does not require Django or Django REST Framework.

It can be used in:

- Django applications
- Flask applications
- FastAPI applications
- CLI applications
- Background workers
- Standalone Python scripts
- Other Python applications

---

# License

This project is licensed under the MIT License.

See the `LICENSE` file for the complete license text.

---

# Author

**Amare Misgana**

---

# Disclaimer

Telebirr and Ethio Telecom are trademarks and services of their respective owners.

This project is an independent Python library and is not affiliated with, endorsed by, or officially supported by Ethio Telecom or Telebirr.

The package retrieves publicly accessible receipt information from the Telebirr transaction information service and provides tools for parsing and verification.

---

# Contributing

Contributions, bug reports, and improvements are welcome.

When submitting an issue, please include:

- Python version
- Package version
- Operating system
- Error message
- Relevant receipt structure information
- Minimal reproducible example

Do not include sensitive personal or financial information in issues or pull requests.

---

# Changelog

## 1.0.0

Initial release.

Features include:

- Telebirr receipt fetching
- Receipt HTML parsing
- Payer information extraction
- Recipient information extraction
- Transaction status extraction
- Payment amount extraction
- Payment verification
- Payer verification
- Recipient verification
- Masked Telebirr number comparison
- Dictionary serialization
- JSON serialization
- Custom exception handling
- HTTP retry support
