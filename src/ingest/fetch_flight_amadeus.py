from __future__ import annotations

import csv
import json
import os
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import mean
from typing import Any
from zoneinfo import ZoneInfo

from amadeus import Client, ResponseError
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# 0) TIME HELPERS
# ============================================================

def today_ny_string() -> str:
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d")


def now_timestamp_string() -> str:
    return datetime.now(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M:%S")


# ============================================================
# 1) CONFIG
# ============================================================

@dataclass(frozen=True)
class Route:
    origin: str
    destination: str
    origin_name: str
    destination_name: str
    origin_country: str
    destination_country: str


ROUTES = [

    Route("CHI", "JFK", "Chicago", "New York", "United States", "United States"), 
    Route("CHI", "ATL", "Chicago", "Atlanta", "United States", "United States"), 

    Route("MIA", "JFK", "Miami", "New York", "United States", "United States"), 

    Route("SEA", "LAX", "Seattle", "Los Angeles", "United States", "United States"),

    Route("BOS", "JFK", "Boston", "New York", "United States", "United States"), 

    Route("LAX", "JFK", "Los Angeles", "New York", "United States", "United States"), 
]

DEPARTURE_DATES: list[str] = [
    "2026-03-13",  # 90 days before
    "2026-05-12",  # 30 days before
    "2026-06-01",  # 10 days before
    "2026-06-10",  # 1 day before
]



ADULTS = 1

# Debug mode: keep request minimal because this is what already worked for you
USE_OPTIONAL_PARAMS = False
CURRENCY_CODE = "USD"
MAX_OFFERS = 20
NON_STOP_ONLY = True

# Delay between requests to reduce 429 risk
REQUEST_SLEEP_SECONDS = 2

# Output folders
BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "bronze"
SUMMARY_DIR = BASE_DIR / "data" / "silver"
LOG_DIR = BASE_DIR / "logs"

RAW_DIR.mkdir(parents=True, exist_ok=True)
SUMMARY_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)


# ============================================================
# 2) AMADEUS CLIENT
# ============================================================

def build_amadeus_client() -> Client:
    """
    Reads credentials from environment variables:
    AMADEUS_API_KEY
    AMADEUS_API_SECRET
    """
    client_id = os.getenv("AMADEUS_API_KEY")
    client_secret = os.getenv("AMADEUS_API_SECRET")

    if not client_id or not client_secret:
        raise EnvironmentError(
            "Missing AMADEUS_API_KEY or AMADEUS_API_SECRET in environment variables."
        )

    return Client(client_id=client_id, client_secret=client_secret)


# ============================================================
# 3) HELPERS
# ============================================================

def safe_float(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def calculate_days_before_departure(search_date_str: str, departure_date_str: str) -> int:
    search_dt = datetime.strptime(search_date_str, "%Y-%m-%d").date()
    depart_dt = datetime.strptime(departure_date_str, "%Y-%m-%d").date()
    return (depart_dt - search_dt).days


def get_stops_count(offer: dict[str, Any]) -> int | None:
    try:
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            return None

        first_itinerary = itineraries[0]
        segments = first_itinerary.get("segments", [])
        if not segments:
            return None

        return max(len(segments) - 1, 0)
    except Exception:
        return None


def get_first_airline_code(offer: dict[str, Any]) -> str | None:
    try:
        itineraries = offer.get("itineraries", [])
        if not itineraries:
            return None

        segments = itineraries[0].get("segments", [])
        if not segments:
            return None

        return segments[0].get("carrierCode")
    except Exception:
        return None


def extract_raw_rows(
    route: Route,
    departure_date: str,
    search_date: str,
    search_timestamp: str,
    offers: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    days_before_departure = calculate_days_before_departure(search_date, departure_date)

    for offer in offers:
        total_price = safe_float(offer.get("price", {}).get("total"))
        currency = offer.get("price", {}).get("currency")
        airline_code = get_first_airline_code(offer)
        stops = get_stops_count(offer)

        row = {
            "search_timestamp": search_timestamp,
            "search_date": search_date,
            "route": f"{route.origin}-{route.destination}",
            "origin": route.origin,
            "destination": route.destination,
            "origin_name": route.origin_name,
            "destination_name": route.destination_name,
            "origin_country": route.origin_country,
            "destination_country": route.destination_country,
            "departure_date": departure_date,
            "days_before_departure": days_before_departure,
            "currency": currency,
            "price_total": total_price,
            "airline_code": airline_code,
            "stops": stops,
            "raw_offer_json": json.dumps(offer, ensure_ascii=False),
        }
        rows.append(row)

    return rows


def summarize_market_prices(
    route: Route,
    departure_date: str,
    search_date: str,
    search_timestamp: str,
    raw_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    all_prices = [
        row["price_total"]
        for row in raw_rows
        if row["price_total"] is not None
    ]

    nonstop_prices = [
        row["price_total"]
        for row in raw_rows
        if row["price_total"] is not None and row["stops"] == 0
    ]

    return {
        "search_timestamp": search_timestamp,
        "search_date": search_date,
        "route": f"{route.origin}-{route.destination}",
        "origin": route.origin,
        "destination": route.destination,
        "departure_date": departure_date,
        "days_before_departure": calculate_days_before_departure(search_date, departure_date),
        "offer_count": len(raw_rows),
        "priced_offer_count": len(all_prices),
        "nonstop_offer_count": len(nonstop_prices),
        "min_price_usd": min(all_prices) if all_prices else None,
        "avg_price_usd": round(mean(all_prices), 2) if all_prices else None,
        "avg_nonstop_price_usd": round(mean(nonstop_prices), 2) if nonstop_prices else None,
    }


def append_rows_to_csv(file_path: Path, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    file_exists = file_path.exists()
    fieldnames = list(rows[0].keys())

    with open(file_path, mode="a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        if not file_exists:
            writer.writeheader()
        writer.writerows(rows)


def append_one_row_to_csv(file_path: Path, row: dict[str, Any]) -> None:
    append_rows_to_csv(file_path, [row])


# ============================================================
# 4) API CALL
# ============================================================

def fetch_flight_offers(
    amadeus: Client,
    origin: str,
    destination: str,
    departure_date: str,
) -> list[dict[str, Any]]:
    """
    During sandbox debugging, keep the request minimal because the
    minimal version already succeeded for BOS -> CHI.
    """
    try:
        if USE_OPTIONAL_PARAMS:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=ADULTS,
                currencyCode=CURRENCY_CODE,
                max=MAX_OFFERS,
                nonStop=NON_STOP_ONLY,
            )
        else:
            response = amadeus.shopping.flight_offers_search.get(
                originLocationCode=origin,
                destinationLocationCode=destination,
                departureDate=departure_date,
                adults=ADULTS,
            )

        return response.data

    except ResponseError as error:
        raise RuntimeError(
            f"Amadeus API error for {origin}-{destination} {departure_date}: {repr(error)}"
        ) from error


# ============================================================
# 5) MAIN PIPELINE
# ============================================================

def run_pipeline() -> None:
    amadeus = build_amadeus_client()

    search_date = today_ny_string()
    search_timestamp = now_timestamp_string()

    raw_output_file = RAW_DIR / f"flight_offers_raw_{search_date}.csv"
    summary_output_file = SUMMARY_DIR / f"flight_market_summary_{search_date}.csv"
    log_file = LOG_DIR / f"run_log_{search_date}.txt"

    success_count = 0
    error_count = 0

    with open(log_file, mode="a", encoding="utf-8") as f:
        f.write(f"\n===== RUN START {search_timestamp} =====\n")
        f.write(f"USE_OPTIONAL_PARAMS={USE_OPTIONAL_PARAMS}\n")
        f.write(f"REQUEST_SLEEP_SECONDS={REQUEST_SLEEP_SECONDS}\n")

    for route in ROUTES:
        for departure_date in DEPARTURE_DATES:
            print(f"Fetching {route.origin}->{route.destination} | departure={departure_date}")

            try:
                offers = fetch_flight_offers(
                    amadeus=amadeus,
                    origin=route.origin,
                    destination=route.destination,
                    departure_date=departure_date,
                )

                if not offers:
                    with open(log_file, mode="a", encoding="utf-8") as f:
                        f.write(
                            f"[NO_OFFERS] {search_timestamp} | {route.origin}-{route.destination} | "
                            f"{departure_date} | offers=0\n"
                        )
                    print(f"No offers for {route.origin}->{route.destination} | {departure_date}")
                    time.sleep(REQUEST_SLEEP_SECONDS)
                    continue

                raw_rows = extract_raw_rows(
                    route=route,
                    departure_date=departure_date,
                    search_date=search_date,
                    search_timestamp=search_timestamp,
                    offers=offers,
                )

                summary_row = summarize_market_prices(
                    route=route,
                    departure_date=departure_date,
                    search_date=search_date,
                    search_timestamp=search_timestamp,
                    raw_rows=raw_rows,
                )

                append_rows_to_csv(raw_output_file, raw_rows)
                append_one_row_to_csv(summary_output_file, summary_row)

                with open(log_file, mode="a", encoding="utf-8") as f:
                    f.write(
                        f"[SUCCESS] {search_timestamp} | {route.origin}-{route.destination} | "
                        f"{departure_date} | offers={len(offers)}\n"
                    )

                success_count += 1

            except Exception as e:
                with open(log_file, mode="a", encoding="utf-8") as f:
                    f.write(
                        f"[ERROR] {search_timestamp} | {route.origin}-{route.destination} | "
                        f"{departure_date} | {repr(e)}\n"
                    )
                print(f"Error for {route.origin}->{route.destination} {departure_date}: {repr(e)}")
                error_count += 1

            time.sleep(REQUEST_SLEEP_SECONDS)

    print("\nRun complete.")
    print(f"Success calls: {success_count}")
    print(f"Error calls:   {error_count}")
    print(f"Raw file:      {raw_output_file}")
    print(f"Summary file:  {summary_output_file}")
    print(f"Log file:      {log_file}")


if __name__ == "__main__":
    run_pipeline()