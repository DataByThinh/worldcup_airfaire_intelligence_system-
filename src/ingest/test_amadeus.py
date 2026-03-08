from amadeus import Client
from dotenv import load_dotenv
import os

# load .env
load_dotenv()

amadeus = Client(
    client_id=os.getenv("AMADEUS_API_KEY"),
    client_secret=os.getenv("AMADEUS_API_SECRET")
)

print("Connected to Amadeus API successfully")

print(os.getenv("AMADEUS_API_KEY"))
print(os.getenv("AMADEUS_API_SECRET"))