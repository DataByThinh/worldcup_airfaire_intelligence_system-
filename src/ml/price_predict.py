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
EVENT_DATE = "2026-06-11"
BOOKING_WINDOWS = [90, 30, 10, 1]

OUTPUT_DIR = "outputs"
os.makedirs(OUTPUT_DIR, exist_ok=True)

#PostgreSQL connection
engine = create_engine(
    "postgresql://postgres:postgres123@localhost:5432/worldcup_airfare_dw"
)

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
    WHERE departure_date = '{EVENT_DATE}'
      AND days_before_event IN (90, 30, 10, 1)
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
df["days_before_event"] = pd.to_numeric(df["days_before_event"], errors="coerce")
df["price_total"] = pd.to_numeric(df["price_total"], errors="coerce")
df["stops"] = pd.to_numeric(df["stops"], errors="coerce")

df = df.dropna().copy()

# keep only exact windows again after coercion
df = df[df["days_before_event"].isin(BOOKING_WINDOWS)].copy()

# Add booking window label
window_label_map = {
    90: "90 days before",
    30: "30 days before",
    10: "10 days before",
    1: "1 day before"
}
df["booking_window"] = df["days_before_event"].map(window_label_map)

print("\n=== CLEANED DATA ===")
print(df.head())
print("Shape:", df.shape)

# =========================================================
# 4. BASIC CHECK: HOW MANY OFFERS BY ROUTE/WINDOW
# =========================================================
offer_check = (
    df.groupby(["route", "days_before_event"], as_index=False)
      .agg(
          offer_count=("price_total", "count"),
          avg_price=("price_total", "mean")
      )
      .sort_values(["route", "days_before_event"], ascending=[True, False])
)

print("\n=== OFFER CHECK ===")
print(offer_check)

offer_check.to_csv(
    os.path.join(OUTPUT_DIR, "offer_check_route_window.csv"),
    index=False
)

# =========================================================
# 5. ROUTE-LEVEL WINDOW ANALYSIS
# Goal: for each route, which booking window is best?
# =========================================================
route_window_stats = (
    df.groupby(["route", "days_before_event", "booking_window"], as_index=False)
      .agg(
          avg_price=("price_total", "mean"),
          median_price=("price_total", "median"),
          min_price=("price_total", "min"),
          max_price=("price_total", "max"),
          offer_count=("price_total", "count"),
          price_std=("price_total", "std")
      )
)

# Fill std NaN if only one record
route_window_stats["price_std"] = route_window_stats["price_std"].fillna(0)

print("\n=== ROUTE WINDOW STATS ===")
print(route_window_stats)

route_window_stats.to_csv(
    os.path.join(OUTPUT_DIR, "route_window_stats.csv"),
    index=False
)

# Best window per route based on lowest average price
best_window_by_route = (
    route_window_stats.sort_values(["route", "avg_price"], ascending=[True, True])
    .groupby("route", as_index=False)
    .first()
    .rename(columns={
        "days_before_event": "best_days_before_event",
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
# 6. AIRLINE ANALYSIS BY ROUTE + WINDOW
# Goal: cheapest airline and most expensive airline
# =========================================================
airline_window_stats = (
    df.groupby(["route", "days_before_event", "booking_window", "airline_code"], as_index=False)
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

# Cheapest airline per route + booking window
cheapest_airline = (
    airline_window_stats.sort_values(
        ["route", "days_before_event", "avg_price"],
        ascending=[True, False, True]
    )
    .groupby(["route", "days_before_event"], as_index=False)
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

# Most expensive airline per route + booking window
most_expensive_airline = (
    airline_window_stats.sort_values(
        ["route", "days_before_event", "avg_price"],
        ascending=[True, False, False]
    )
    .groupby(["route", "days_before_event"], as_index=False)
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
    on=["route", "days_before_event"],
    how="inner"
)

# keep one window label
route_window_airline_summary["booking_window"] = route_window_airline_summary["window_label"]
route_window_airline_summary = route_window_airline_summary.drop(
    columns=["window_label_exp", "window_label"]
)

print("\n=== ROUTE + WINDOW + AIRLINE SUMMARY ===")
print(route_window_airline_summary)

route_window_airline_summary.to_csv(
    os.path.join(OUTPUT_DIR, "route_window_airline_summary.csv"),
    index=False
)

# =========================================================
# 7. FINAL BUSINESS SUMMARY
# Goal:
# - best booking window for each route
# - within that best window, cheapest and most expensive airline
# =========================================================
final_business_summary = best_window_by_route.merge(
    route_window_airline_summary,
    left_on=["route", "best_days_before_event"],
    right_on=["route", "days_before_event"],
    how="left"
)

print("\n=== FINAL BUSINESS SUMMARY ===")
print(final_business_summary)

final_business_summary.to_csv(
    os.path.join(OUTPUT_DIR, "final_business_summary.csv"),
    index=False
)

# =========================================================
# 8. OPTIONAL: ROUTE-WINDOW HEATMAP-LIKE TABLE
# =========================================================
pivot_avg_price = route_window_stats.pivot_table(
    index="route",
    columns="days_before_event",
    values="avg_price"
)

# reorder columns
pivot_avg_price = pivot_avg_price.reindex(columns=[90, 30, 10, 1])

print("\n=== PIVOT AVG PRICE BY ROUTE / WINDOW ===")
print(pivot_avg_price)

pivot_avg_price.to_csv(
    os.path.join(OUTPUT_DIR, "pivot_avg_price_by_route_window.csv")
)

# =========================================================
# 9. CHARTS FOR EACH ROUTE
# =========================================================
unique_routes = sorted(df["route"].unique())

for route_name in unique_routes:
    plot_df = (
        route_window_stats[route_window_stats["route"] == route_name]
        .sort_values("days_before_event", ascending=False)
    )

    plt.figure(figsize=(8, 5))
    plt.plot(plot_df["days_before_event"], plot_df["avg_price"], marker="o")
    plt.xlabel("Days Before Event")
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
# 10. OPTIONAL: SCORE BOOKING WINDOWS
# Lower price = better score
# =========================================================
# Route-level ranking of all 4 windows
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
# 11. CLEAN PRESENTATION TABLE
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
# 12. DONE
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