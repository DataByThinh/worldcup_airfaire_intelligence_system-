import os
import pandas as pd
import numpy as np
from sqlalchemy import create_engine
import matplotlib
matplotlib.use("Agg", force=True)
import matplotlib.pyplot as plt

# =========================================================
# 1. CONFIG
# =========================================================
OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

engine = create_engine(
    "postgresql://postgres:postgres123@localhost:5432/worldcup_airfare_dw")
EVENT_DATE = "2026-06-11"

# These are the exact dates you have in your data
SEARCH_DATE_TO_WINDOW = {
    "2026-03-13": 90,
    "2026-05-12": 30,
    "2026-06-01": 10,
    "2026-06-10": 1
}

WINDOW_LABEL_MAP = {
    90: "90 days before",
    30: "30 days before",
    10: "10 days before",
    1: "1 day before"
}

SELECTED_SEARCH_DATES = list(SEARCH_DATE_TO_WINDOW.keys())

# =========================================================
# 2. LOAD DATA
# =========================================================
query = f"""
    SELECT
        route,
        departure_date,
        search_date,
        days_before_event,
        price_total,
        airline_code,
        stops
    FROM silver.flight_prices_clean
    WHERE search_date IN ({",".join([f"'{d}'" for d in SELECTED_SEARCH_DATES])})
"""

df = pd.read_sql(query, engine)

print("=== RAW DATA LOADED ===")
print(df.head())
print("Shape:", df.shape)
print(df.info())
print(df.isnull().sum())

# =========================================================
# 3. CLEAN DATA
# =========================================================
df = df.dropna().copy()

df["departure_date"] = pd.to_datetime(df["departure_date"])
df["search_date"] = pd.to_datetime(df["search_date"])
df["price_total"] = pd.to_numeric(df["price_total"], errors="coerce")
df["stops"] = pd.to_numeric(df["stops"], errors="coerce")

df = df.dropna().copy()

# Convert search_date back to string for mapping
df["search_date_str"] = df["search_date"].dt.strftime("%Y-%m-%d")

# Assign the exact booking windows based on the selected dates
df["booking_window_days"] = df["search_date_str"].map(SEARCH_DATE_TO_WINDOW)
df["booking_window"] = df["booking_window_days"].map(WINDOW_LABEL_MAP)

# Keep only rows that matched the mapping
df = df.dropna(subset=["booking_window_days", "booking_window"]).copy()
df["booking_window_days"] = df["booking_window_days"].astype(int)

print("\n=== CLEANED DATA ===")
print(df.head())
print("Shape:", df.shape)
print("\nUnique search dates:", sorted(df["search_date_str"].unique()))
print("Unique booking windows:", sorted(df["booking_window_days"].unique(), reverse=True))

# =========================================================
# 4. CHECK DATA COVERAGE
# =========================================================
offer_check = (
    df.groupby(["route", "search_date_str", "booking_window_days", "booking_window"], as_index=False)
      .agg(
          offer_count=("price_total", "count"),
          avg_price=("price_total", "mean")
      )
      .sort_values(["route", "booking_window_days"], ascending=[True, False])
)

print("\n=== OFFER CHECK ===")
print(offer_check)

offer_check.to_csv(
    os.path.join(OUTPUT_DIR, "offer_check_route_window.csv"),
    index=False
)

# =========================================================
# 5. ROUTE + WINDOW STATS
# Goal: which booking window is best for each route?
# =========================================================
route_window_stats = (
    df.groupby(["route", "booking_window_days", "booking_window"], as_index=False)
      .agg(
          avg_price=("price_total", "mean"),
          median_price=("price_total", "median"),
          min_price=("price_total", "min"),
          max_price=("price_total", "max"),
          offer_count=("price_total", "count"),
          price_std=("price_total", "std")
      )
)

route_window_stats["price_std"] = route_window_stats["price_std"].fillna(0)

print("\n=== ROUTE WINDOW STATS ===")
print(route_window_stats)

route_window_stats.to_csv(
    os.path.join(OUTPUT_DIR, "route_window_stats.csv"),
    index=False
)

# =========================================================
# 6. BEST WINDOW BY ROUTE
# =========================================================
best_window_by_route = (
    route_window_stats.sort_values(["route", "avg_price"], ascending=[True, True])
    .groupby("route", as_index=False)
    .first()
    .rename(columns={
        "booking_window_days": "best_days_before_event",
        "booking_window": "best_booking_window",
        "avg_price": "best_window_avg_price",
        "median_price": "best_window_median_price",
        "min_price": "best_window_min_price",
        "max_price": "best_window_max_price",
        "offer_count": "best_window_offer_count",
        "price_std": "best_window_price_std"
    })
)

print("\n=== BEST WINDOW BY ROUTE ===")
print(best_window_by_route)

best_window_by_route.to_csv(
    os.path.join(OUTPUT_DIR, "best_window_by_route.csv"),
    index=False
)

# =========================================================
# 7. AIRLINE STATS BY ROUTE + WINDOW
# Goal: cheapest and most expensive airline in each route/window
# =========================================================
airline_window_stats = (
    df.groupby(["route", "booking_window_days", "booking_window", "airline_code"], as_index=False)
      .agg(
          avg_price=("price_total", "mean"),
          median_price=("price_total", "median"),
          min_price=("price_total", "min"),
          max_price=("price_total", "max"),
          offer_count=("price_total", "count")
      )
)

print("\n=== AIRLINE WINDOW STATS ===")
print(airline_window_stats.head(20))

airline_window_stats.to_csv(
    os.path.join(OUTPUT_DIR, "airline_window_stats.csv"),
    index=False
)

# Cheapest airline per route + window
cheapest_airline = (
    airline_window_stats.sort_values(
        ["route", "booking_window_days", "avg_price"],
        ascending=[True, False, True]
    )
    .groupby(["route", "booking_window_days"], as_index=False)
    .first()
    .rename(columns={
        "booking_window": "window_label",
        "airline_code": "cheapest_airline",
        "avg_price": "cheapest_avg_price",
        "median_price": "cheapest_median_price",
        "min_price": "cheapest_min_price",
        "max_price": "cheapest_max_price",
        "offer_count": "cheapest_offer_count"
    })
)

# Most expensive airline per route + window
most_expensive_airline = (
    airline_window_stats.sort_values(
        ["route", "booking_window_days", "avg_price"],
        ascending=[True, False, False]
    )
    .groupby(["route", "booking_window_days"], as_index=False)
    .first()
    .rename(columns={
        "booking_window": "window_label_exp",
        "airline_code": "most_expensive_airline",
        "avg_price": "most_expensive_avg_price",
        "median_price": "most_expensive_median_price",
        "min_price": "most_expensive_min_price",
        "max_price": "most_expensive_max_price",
        "offer_count": "most_expensive_offer_count"
    })
)

route_window_airline_summary = cheapest_airline.merge(
    most_expensive_airline,
    on=["route", "booking_window_days"],
    how="inner"
)

route_window_airline_summary["booking_window"] = route_window_airline_summary["window_label"]
route_window_airline_summary = route_window_airline_summary.drop(
    columns=["window_label", "window_label_exp"]
)

print("\n=== ROUTE WINDOW AIRLINE SUMMARY ===")
print(route_window_airline_summary)

route_window_airline_summary.to_csv(
    os.path.join(OUTPUT_DIR, "route_window_airline_summary.csv"),
    index=False
)

# =========================================================
# 8. FINAL BUSINESS SUMMARY
# =========================================================
final_business_summary = best_window_by_route.merge(
    route_window_airline_summary,
    left_on=["route", "best_days_before_event"],
    right_on=["route", "booking_window_days"],
    how="left"
)

print("\n=== FINAL BUSINESS SUMMARY ===")
print(final_business_summary)

final_business_summary.to_csv(
    os.path.join(OUTPUT_DIR, "final_business_summary.csv"),
    index=False
)

# =========================================================
# 9. PIVOT TABLE FOR DASHBOARD
# =========================================================
pivot_avg_price = route_window_stats.pivot_table(
    index="route",
    columns="booking_window_days",
    values="avg_price"
)

pivot_avg_price = pivot_avg_price.reindex(columns=[90, 30, 10, 1])

print("\n=== PIVOT AVG PRICE BY ROUTE / WINDOW ===")
print(pivot_avg_price)

pivot_avg_price.to_csv(
    os.path.join(OUTPUT_DIR, "pivot_avg_price_by_route_window.csv")
)

# =========================================================
# 10. WINDOW RANKING BY ROUTE
# =========================================================
window_ranking = (
    route_window_stats.sort_values(["route", "avg_price"], ascending=[True, True])
    .groupby("route", group_keys=False)
    .apply(lambda x: x.assign(window_rank=np.arange(1, len(x) + 1)))
    .reset_index(drop=True)
)

print("\n=== WINDOW RANKING BY ROUTE ===")
print(window_ranking)

window_ranking.to_csv(
    os.path.join(OUTPUT_DIR, "window_ranking_by_route.csv"),
    index=False
)

# =========================================================
# 11. PRESENTATION TABLE
# =========================================================
presentation_table = final_business_summary[[
    "route",
    "best_days_before_event",
    "best_booking_window",
    "best_window_avg_price",
    "cheapest_airline",
    "cheapest_avg_price",
    "most_expensive_airline",
    "most_expensive_avg_price"
]].sort_values("route")

print("\n=== PRESENTATION TABLE ===")
print(presentation_table)

presentation_table.to_csv(
    os.path.join(OUTPUT_DIR, "presentation_table.csv"),
    index=False
)

# =========================================================
# 12. CHARTS
# =========================================================
unique_routes = sorted(df["route"].unique())

for route_name in unique_routes:
    plot_df = (
        route_window_stats[route_window_stats["route"] == route_name]
        .sort_values("booking_window_days", ascending=False)
    )

    plt.figure(figsize=(8, 5))
    plt.plot(plot_df["booking_window_days"], plot_df["avg_price"], marker="o")
    plt.xlabel("Booking Window (Days Before Event)")
    plt.ylabel("Average Price")
    plt.title(f"Average Price by Booking Window - {route_name}")
    plt.grid(True)
    plt.savefig(
        os.path.join(OUTPUT_DIR, f"route_window_chart_{route_name}.png"),
        dpi=300,
        bbox_inches="tight"
    )
    plt.close()

print("\nSaved route-level charts.")

# =========================================================
# 13. DONE
# =========================================================
print("\n=== DONE ===")
print("Generated files:")
print("- outputs/offer_check_route_window.csv")
print("- outputs/route_window_stats.csv")
print("- outputs/best_window_by_route.csv")
print("- outputs/airline_window_stats.csv")
print("- outputs/route_window_airline_summary.csv")
print("- outputs/final_business_summary.csv")
print("- outputs/pivot_avg_price_by_route_window.csv")
print("- outputs/window_ranking_by_route.csv")
print("- outputs/presentation_table.csv")
print("- outputs/route_window_chart_<route>.png")