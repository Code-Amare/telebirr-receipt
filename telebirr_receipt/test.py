import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telebirr_receipt.tele import (
    TelebirrReceipt,
    ReceiptNotFoundError,
    TelebirrFetchError,
    TelebirrError,
)

receipt = TelebirrReceipt("DDS9AU8WR7")

try:
    receipt.load()
except ReceiptNotFoundError:
    print("Receipt not found – invalid or expired.")
except TelebirrFetchError as e:
    print(f"Network/HTTP error: {e}")
except TelebirrError as e:
    print(f"Other telebirr error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

print(receipt.payer_name)
print(receipt.payer_telebirr_no)
print(
    receipt.verify_payment(
        expected_payer_number="2519****6652", expected_recipient_number="2519****0888"
    )
)
