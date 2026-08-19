import requests

receipt_id = "DDS9AU8WR7"

url = f"https://transactioninfo.ethiotelecom.et/receipt/{receipt_id}"

response = requests.get(
    url,
    headers={
        "User-Agent": "Mozilla/5.0",
    },
    timeout=15,
)

response.raise_for_status()

print(response.text)
