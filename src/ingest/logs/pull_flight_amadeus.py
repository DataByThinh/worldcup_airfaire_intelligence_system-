import os
from dotenv import load_dotenv
from amadeus import Client, ResponseError

load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET"),
)

try:
    response = amadeus.shopping.flight_offers_search.get(
        originLocationCode="BOS",
        destinationLocationCode="CHI",
        departureDate="2026-03-20",
        adults=1
    )
    print("SUCCESS")
    print(response.data[:1])
except ResponseError as e:
    print("ERROR")
    print(repr(e))