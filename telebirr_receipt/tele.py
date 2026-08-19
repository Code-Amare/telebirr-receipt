import json
import logging
import re
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, Any

import requests
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from requests.exceptions import RequestException
from urllib3.util.retry import Retry

logger = logging.getLogger(__name__)

BASE_URL = "https://transactioninfo.ethiotelecom.et/receipt/{}"


class TelebirrError(Exception):
    """Base exception for telebirr_receipt."""


class TelebirrFetchError(TelebirrError):
    """Raised when the receipt cannot be fetched."""


class TelebirrParseError(TelebirrError):
    """Raised when the receipt HTML cannot be parsed."""


class ReceiptNotFoundError(TelebirrError):
    """Raised when the receipt does not exist or has no transaction data."""


class PaymentVerificationError(TelebirrError):
    """Raised when payment verification fails."""


@dataclass
class TelebirrReceipt:
    receipt_no: Optional[str] = None
    payer_name: Optional[str] = None
    payer_telebirr_no: Optional[str] = None
    payer_account_type: Optional[str] = None
    payer_tin_no: Optional[str] = None
    payer_vat_reg_no: Optional[str] = None
    payer_vat_reg_date: Optional[str] = None

    credited_party_name: Optional[str] = None
    credited_party_account_no: Optional[str] = None

    transaction_status: Optional[str] = None
    payment_date: Optional[str] = None
    settled_amount_raw: Optional[str] = None
    settled_amount: Optional[float] = None

    stamp_duty_raw: Optional[str] = None
    stamp_duty: Optional[float] = None

    discount_amount_raw: Optional[str] = None
    discount_amount: Optional[float] = None

    service_fee_raw: Optional[str] = None
    service_fee: Optional[float] = None

    service_fee_vat_raw: Optional[str] = None
    service_fee_vat: Optional[float] = None

    total_paid_amount_raw: Optional[str] = None
    total_paid_amount: Optional[float] = None

    total_amount_in_words: Optional[str] = None

    payment_mode: Optional[str] = None
    payment_reason: Optional[str] = None
    payment_channel: Optional[str] = None
    customer_note: Optional[str] = None

    raw_pairs: Dict[str, str] = field(default_factory=dict)
    fetched_at: Optional[str] = None

    # ------------------------------------------------------------------
    # Helper methods
    # ------------------------------------------------------------------
    @staticmethod
    def _clean(value: Optional[str]) -> Optional[str]:
        """Normalize whitespace and return None for empty strings."""
        if not value:
            return None
        value = re.sub(r"\s+", " ", str(value)).strip()
        return value or None

    @staticmethod
    def _parse_amount(value: Optional[str]) -> Optional[float]:
        """Extract a float from strings like '50 Birr', '0.87 Birr', '1,234.56'."""
        if not value:
            return None
        match = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", str(value))
        if not match:
            return None
        try:
            return float(match.group().replace(",", ""))
        except ValueError:
            return None

    @staticmethod
    def _masked_number_matches(masked: Optional[str], full: Optional[str]) -> bool:
        """
        Compare a telebirr masked number (e.g. '2519****6652')
        with a full number (e.g. '251912346652').
        Supports numbers without asterisks as well.
        """
        if not masked or not full:
            return False

        masked_clean = re.sub(r"\s+", "", masked)
        full_clean = re.sub(r"\s+", "", full)

        if "*" not in masked_clean:
            return masked_clean == full_clean

        # If both are masked, compare them directly.
        if "*" in full_clean:
            return masked_clean == full_clean

        parts = masked_clean.split("*")
        prefix = parts[0]
        suffix = parts[-1]

        if prefix and not full_clean.startswith(prefix):
            return False

        if suffix and not full_clean.endswith(suffix):
            return False

        return True

    # ------------------------------------------------------------------
    # HTTP fetching
    # ------------------------------------------------------------------
    def fetch(self) -> str:
        """Fetch the receipt HTML from telebirr."""
        receipt_no = (self.receipt_no or "").strip()
        if not receipt_no:
            raise TelebirrFetchError("receipt_no is required")

        # Keep a clean receipt number internally.
        self.receipt_no = receipt_no

        url = BASE_URL.format(receipt_no)
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        }

        session = requests.Session()
        retry_strategy = Retry(
            total=3,
            backoff_factor=1.5,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        try:
            response = session.get(
                url,
                headers=headers,
                timeout=(5, 15),
                verify=True,  # Never silently disable TLS verification.
            )
        except RequestException as exc:
            raise TelebirrFetchError(
                f"Failed to fetch telebirr receipt {receipt_no}: {exc}"
            ) from exc
        finally:
            session.close()

        if response.status_code == 404:
            raise ReceiptNotFoundError(f"Receipt {receipt_no} not found (HTTP 404)")

        if response.status_code != 200:
            raise TelebirrFetchError(
                f"Telebirr returned HTTP {response.status_code} for {receipt_no}"
            )

        return response.text

    # ------------------------------------------------------------------
    # Parsing
    # ------------------------------------------------------------------
    def parse(self, html: str) -> "TelebirrReceipt":
        """Parse receipt HTML and populate this dataclass."""
        if not html or not html.strip():
            raise TelebirrParseError("Received empty HTML")

        soup = BeautifulSoup(html, "html.parser")
        self.raw_pairs.clear()

        data = {
            "receipt_no": None,
            "payer_name": None,
            "payer_telebirr_no": None,
            "payer_account_type": None,
            "payer_tin_no": None,
            "payer_vat_reg_no": None,
            "payer_vat_reg_date": None,
            "credited_party_name": None,
            "credited_party_account_no": None,
            "transaction_status": None,
            "payment_date": None,
            "settled_amount_raw": None,
            "stamp_duty_raw": None,
            "discount_amount_raw": None,
            "service_fee_raw": None,
            "service_fee_vat_raw": None,
            "total_paid_amount_raw": None,
            "total_amount_in_words": None,
            "payment_mode": None,
            "payment_reason": None,
            "payment_channel": None,
            "customer_note": None,
        }

        # Label mapping. Keys have no periods so matching is more forgiving.
        label_map = {
            "payer name": "payer_name",
            "payer telebirr no": "payer_telebirr_no",
            "payer account type": "payer_account_type",
            "payer tin no": "payer_tin_no",
            "payer vat reg no": "payer_vat_reg_no",
            "vat reg no": "payer_vat_reg_no",
            "payer vat reg date": "payer_vat_reg_date",
            "vat reg date": "payer_vat_reg_date",
            "credited party name": "credited_party_name",
            "credited party account no": "credited_party_account_no",
            "transaction status": "transaction_status",
            "stamp duty": "stamp_duty_raw",
            "discount amount": "discount_amount_raw",
            "service fee vat": "service_fee_vat_raw",
            "service fee": "service_fee_raw",
            "total paid amount": "total_paid_amount_raw",
            "total amount in word": "total_amount_in_words",
            "payment mode": "payment_mode",
            "payment reason": "payment_reason",
            "payment channel": "payment_channel",
            "customer note": "customer_note",
        }

        label_keys = sorted(label_map.keys(), key=len, reverse=True)

        def normalize_label(label: str) -> str:
            """Extract the English part of a label like 'የከፋይ ስም/Payer Name'."""
            label = self._clean(label) or ""
            if "/" in label:
                parts = [p.strip() for p in label.split("/")]
                english_parts = [p for p in parts if re.search(r"[A-Za-z]", p)]
                if english_parts:
                    return english_parts[-1]
            return label

        def match_key(normalized_label: str) -> Optional[str]:
            normalized = (
                normalized_label.lower().replace(".", "").replace("_", " ").strip()
            )
            for key in label_keys:
                # Keys are already without dots/underscores.
                if key in normalized:
                    return label_map[key]
            return None

        def extract_pairs_from_elements(elements) -> None:
            """Walk td/th elements in order and pair labels with the next value."""
            i = 0
            while i < len(elements):
                label_text = self._clean(elements[i].get_text(" ", strip=True))
                norm = normalize_label(label_text) if label_text else ""
                key = match_key(norm) if norm else None

                if not key:
                    i += 1
                    continue

                value_text = None
                if i + 1 < len(elements):
                    next_text = self._clean(elements[i + 1].get_text(" ", strip=True))
                    next_norm = normalize_label(next_text) if next_text else ""

                    if next_text and not match_key(next_norm):
                        value_text = next_text
                        i += 2
                    elif not next_text:
                        # Empty value cell, skip it.
                        i += 2
                    else:
                        # Next cell is another label, so current field has no value.
                        i += 1
                else:
                    i += 1

                data[key] = value_text
                if value_text is not None:
                    self.raw_pairs[norm] = value_text

        def find_leaf_table(*texts):
            """
            Find the smallest/deepest table that contains all given texts.
            This avoids picking the outer wrapper table.
            """
            candidates = []
            for table in soup.find_all("table"):
                table_text = table.get_text(" ", strip=True)
                if all(t.lower() in table_text.lower() for t in texts):
                    candidates.append(table)

            if not candidates:
                return None

            return min(candidates, key=lambda t: len(t.find_all("table")))

        # ------------------------------------------------------------------
        # Payer / transaction table
        # ------------------------------------------------------------------
        payer_table = find_leaf_table("Payer Name", "transaction status")
        if payer_table:
            extract_pairs_from_elements(payer_table.find_all(["td", "th"]))
        else:
            logger.warning("Payer/transaction table not found")

        # ------------------------------------------------------------------
        # Invoice details table
        # ------------------------------------------------------------------
        invoice_table = find_leaf_table("Invoice details")
        if invoice_table:
            rows = invoice_table.find_all("tr")
            header_idx = None
            value_idx = None

            for i, row in enumerate(rows):
                cells = row.find_all(["td", "th"])
                texts = [
                    self._clean(cell.get_text(" ", strip=True)) or "" for cell in cells
                ]
                joined = " ".join(texts).lower()

                if (
                    "invoice no" in joined
                    and "payment date" in joined
                    and "settled amount" in joined
                ):
                    header_idx = i
                    value_idx = i + 1 if i + 1 < len(rows) else None
                    break

            if header_idx is not None and value_idx is not None:
                value_cells = rows[value_idx].find_all(["td", "th"])
                if len(value_cells) >= 3:
                    data["receipt_no"] = self._clean(
                        value_cells[0].get_text(" ", strip=True)
                    )
                    data["payment_date"] = self._clean(
                        value_cells[1].get_text(" ", strip=True)
                    )
                    data["settled_amount_raw"] = self._clean(
                        value_cells[2].get_text(" ", strip=True)
                    )

                    self.raw_pairs["Invoice No."] = data["receipt_no"]
                    self.raw_pairs["Payment date"] = data["payment_date"]
                    self.raw_pairs["Settled Amount"] = data["settled_amount_raw"]
                else:
                    logger.warning("Invoice value row did not contain 3 columns")

                # Parse the remaining fee rows after the header/value rows.
                fee_elements = []
                for row in rows[value_idx + 1 :]:
                    fee_elements.extend(row.find_all(["td", "th"]))
                extract_pairs_from_elements(fee_elements)
            else:
                logger.warning("Invoice header row not found")
        else:
            logger.warning("Invoice details table not found")

        # ------------------------------------------------------------------
        # Payment info table
        # ------------------------------------------------------------------
        payment_info_table = find_leaf_table("Total Amount in word")
        if payment_info_table:
            extract_pairs_from_elements(payment_info_table.find_all(["td", "th"]))
        else:
            logger.warning("Payment info table not found")

        # ------------------------------------------------------------------
        # Validate and populate dataclass
        # ------------------------------------------------------------------
        if not data["receipt_no"]:
            raise ReceiptNotFoundError(
                "Could not find receipt number in HTML. "
                "The receipt may be invalid or the page structure changed."
            )

        for field_name, value in data.items():
            setattr(self, field_name, value)

        # Convert raw amounts to floats.
        self.settled_amount = self._parse_amount(self.settled_amount_raw)
        self.stamp_duty = self._parse_amount(self.stamp_duty_raw)
        self.discount_amount = self._parse_amount(self.discount_amount_raw)
        self.service_fee = self._parse_amount(self.service_fee_raw)
        self.service_fee_vat = self._parse_amount(self.service_fee_vat_raw)
        self.total_paid_amount = self._parse_amount(self.total_paid_amount_raw)

        self.fetched_at = time.strftime("%Y-%m-%dT%H:%M:%S")

        return self

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def load(self) -> "TelebirrReceipt":
        """Fetch and parse the receipt."""
        html = self.fetch()
        self.parse(html)
        return self

    def exists(self) -> bool:
        """Return True if the receipt exists on telebirr."""
        try:
            self.load()
            return bool(self.receipt_no)
        except (TelebirrError, RequestException):
            return False

    def is_completed(self) -> bool:
        """Check if transaction status is 'Completed'."""
        if self.transaction_status is None:
            self.load()
        return (self.transaction_status or "").strip().lower() == "completed"

    def get_amount(self) -> Optional[float]:
        """Return the total paid amount (numeric)."""
        if self.total_paid_amount is None and self.total_paid_amount_raw:
            self.total_paid_amount = self._parse_amount(self.total_paid_amount_raw)
        return self.total_paid_amount

    def get_settled_amount(self) -> Optional[float]:
        """Return the settled amount (numeric)."""
        if self.settled_amount is None and self.settled_amount_raw:
            self.settled_amount = self._parse_amount(self.settled_amount_raw)
        return self.settled_amount

    def get_payer_name(self) -> Optional[str]:
        return self.payer_name

    def get_payer_number(self) -> Optional[str]:
        return self.payer_telebirr_no

    def get_recipient_name(self) -> Optional[str]:
        return self.credited_party_name

    def get_recipient_number(self) -> Optional[str]:
        return self.credited_party_account_no

    def check_recipient(
        self,
        name: str,
        number: str,
        ignore_case: bool = True,
    ) -> bool:
        """
        Verify that the receipt's credited party matches the given name
        and telebirr number. The number supports masked comparison.
        """
        if not name or not number:
            raise ValueError("Recipient name and number are required")

        if self.credited_party_name is None:
            self.load()

        actual_name = self.credited_party_name or ""
        actual_number = self.credited_party_account_no or ""

        if ignore_case:
            name_matches = actual_name.strip().casefold() == name.strip().casefold()
        else:
            name_matches = actual_name.strip() == name.strip()

        number_matches = self._masked_number_matches(actual_number, number)

        return name_matches and number_matches

    def check_payer(
        self,
        name: str,
        number: str,
        ignore_case: bool = True,
    ) -> bool:
        """Verify that the receipt's payer matches the given name and number."""
        if not name or not number:
            raise ValueError("Payer name and number are required")

        if self.payer_name is None:
            self.load()

        actual_name = self.payer_name or ""
        actual_number = self.payer_telebirr_no or ""

        if ignore_case:
            name_matches = actual_name.strip().casefold() == name.strip().casefold()
        else:
            name_matches = actual_name.strip() == name.strip()

        number_matches = self._masked_number_matches(actual_number, number)

        return name_matches and number_matches

    def verify_payment(
        self,
        expected_recipient_name: Optional[str] = None,
        expected_recipient_number: Optional[str] = None,
        expected_payer_name: Optional[str] = None,
        expected_payer_number: Optional[str] = None,
        expected_amount: Optional[float] = None,
        expected_status: str = "Completed",
        amount_tolerance: float = 0.0,
    ) -> Dict[str, Any]:
        """
        Perform full verification.
        Returns a dict with the result and detailed checks.
        """
        if not self.receipt_no:
            raise ValueError("receipt_no must be set before verification")

        if self.payer_name is None:
            self.load()

        checks = {}
        errors = {}

        # Status
        actual_status = (self.transaction_status or "").strip().lower()
        checks["status"] = actual_status == expected_status.strip().lower()
        if not checks["status"]:
            errors["status"] = (
                f"Expected status '{expected_status}', "
                f"got '{self.transaction_status}'"
            )

        # Amount
        if expected_amount is not None:
            actual_amount = self.get_amount()
            if actual_amount is None:
                checks["amount"] = False
                errors["amount"] = "Receipt does not contain a total paid amount"
            else:
                checks["amount"] = (
                    abs(actual_amount - expected_amount) <= amount_tolerance
                )
                if not checks["amount"]:
                    errors["amount"] = (
                        f"Expected amount {expected_amount}, got {actual_amount}"
                    )

        # Payer name
        if expected_payer_name:
            actual_payer = self.payer_name or ""
            expected_payer_clean = expected_payer_name.strip()
            payer_name_match = (
                actual_payer.strip().casefold() == expected_payer_clean.casefold()
            )
            checks["payer_name"] = payer_name_match
            if not payer_name_match:
                errors["payer_name"] = (
                    f"Expected payer '{expected_payer_name}', "
                    f"got '{self.payer_name}'"
                )

        # Payer number (masked)
        if expected_payer_number:
            payer_num_match = self._masked_number_matches(
                self.payer_telebirr_no,
                expected_payer_number,
            )
            checks["payer_number"] = payer_num_match
            if not payer_num_match:
                errors["payer_number"] = (
                    f"Payer number mismatch for "
                    f"'{self.payer_telebirr_no}' vs '{expected_payer_number}'"
                )

        # Recipient name
        if expected_recipient_name:
            actual_recipient = self.credited_party_name or ""
            expected_recipient_clean = expected_recipient_name.strip()
            recipient_name_match = (
                actual_recipient.strip().casefold()
                == expected_recipient_clean.casefold()
            )
            checks["recipient_name"] = recipient_name_match
            if not recipient_name_match:
                errors["recipient_name"] = (
                    f"Expected recipient '{expected_recipient_name}', "
                    f"got '{self.credited_party_name}'"
                )

        # Recipient number (masked)
        if expected_recipient_number:
            recipient_num_match = self._masked_number_matches(
                self.credited_party_account_no,
                expected_recipient_number,
            )
            checks["recipient_number"] = recipient_num_match
            if not recipient_num_match:
                errors["recipient_number"] = (
                    f"Recipient number mismatch for "
                    f"'{self.credited_party_account_no}' "
                    f"vs '{expected_recipient_number}'"
                )

        is_valid = all(checks.values()) if checks else True

        return {
            "valid": is_valid,
            "receipt_no": self.receipt_no,
            "status": self.transaction_status,
            "amount": self.get_amount(),
            "recipient": {
                "name": self.credited_party_name,
                "number": self.credited_party_account_no,
            },
            "payer": {
                "name": self.payer_name,
                "number": self.payer_telebirr_no,
            },
            "checks": checks,
            "errors": errors,
        }

    # ------------------------------------------------------------------
    # Serialization
    # ------------------------------------------------------------------
    def to_dict(self) -> Dict[str, Any]:
        """Return all fields as a dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Return JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)

    def __repr__(self) -> str:
        return f"<TelebirrReceipt {self.receipt_no}>"
