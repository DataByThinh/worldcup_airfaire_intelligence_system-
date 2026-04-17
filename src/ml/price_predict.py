import pandas as pd
from sqlalchemy import create_engine

engine = create_engine(
    "postgresql://postgres:postgres123@localhost:5432/worldcup_airfare_dw"
)

# Pull from your silver layer
df = pd.read_sql("""
    SELECT route, departure_date, search_date,
           days_before_event, price_total,
           airline_code, stops
    FROM silver.flight_prices_clean
    WHERE departure_date IN ('2026-03-13','2026-05-12','2026-06-01','2026-06-10')
""", engine)

print("Data loaded successfully!")
print(df.head())
print(df.shape)