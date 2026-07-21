import argparse
import json
import logging
from datetime import datetime, timezone
from pathlib import Path

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s",
)
logger = logging.getLogger(__name__)

API_URL = "https://open.er-api.com/v6/latest/{base}"

def fetch_rates(base_currency: str) -> dict:
    """Fetch latest exchange rates for a given base currency."""
    url = API_URL.format(base=base_currency)
    logger.info(f"Fetching rates from {url}")

    response = requests.get(url, timeout=10)
    response.raise_for_status()
    data = response.json()

    if data.get("result") !="success":
        raise ValueError(f"API returned non-success result: {data}")
    
    return data

def save_raw(data: dict, output_dir: str, base_currency:str) -> Path:
    """Persist raw API response to the bronze layer, partitioned by ingestion date."""
    ingested_at = datetime.now(timezone.utc)
    date_partition = ingested_at.strftime("%Y-%m-%d")

    out_path = Path(output_dir) / date_partition
    out_path.mkdir(parents=True, exist_ok=True)

    file_path = out_path / f"{base_currency}_{ingested_at.strftime('%H%M%S')}.json"

    payload = {
        "source": "open.er-api.com",
        "base_currency": base_currency,
        "ingested_at": ingested_at.isoformat(),
        "raw_response": data,
    }

    with open(file_path, "w") as f:
        json.dump(payload, f, indent=2)

    logger.info(f"Saved raw data to {file_path}")
    return file_path

def main():
    parser = argparse.ArgumentParser(description="Fetch exchange rates into bronze layer")
    parser.add_argument("--base", default="USD", help="Base currency code, e.g. USD, EUR")
    parser.add_argument(
        "--output-dir",
        default="data/bronze/exchange_rates",
        help="Directory to land raw JSON files",
    )
    args = parser.parse_args()

    data = fetch_rates(args.base)
    save_raw(data, args.output_dir, args.base)
    logger.info("Ingestion completed successfully")

if __name__=="__main__":
    main() 