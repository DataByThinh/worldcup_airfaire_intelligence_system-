"""
World Cup Airfare Intelligence System
======================================
Portfolio project: ML-powered airfare prediction + recommendation engine
for FIFA World Cup 2026.

Author: [Your Name]
Data: Snapshot-based PostgreSQL airfare data (4 booking windows)
Model: XGBoost regression — price_total as target
Output: Predicted prices + traveler recommendations per route
"""

import pandas as pd
import numpy as np
from sqlalchemy import create_engine
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import cross_val_score
from sklearn.metrics import mean_absolute_error, r2_score
import xgboost as xgb
import warnings
warnings.filterwarnings("ignore")

# ─────────────────────────────────────────────
# 1. DATABASE CONNECTION & DATA PULL
# ─────────────────────────────────────────────
import os
from dotenv import load_dotenv

load_dotenv()

DB_CONFIG = {
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
    "database": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
}

def get_engine():
    url = (
        f"postgresql+psycopg2://{DB_CONFIG['user']}:{DB_CONFIG['password']}"
        f"@{DB_CONFIG['host']}:{DB_CONFIG['port']}/{DB_CONFIG['database']}"
    )
    return create_engine(url)


def pull_data(engine) -> pd.DataFrame:
    query = """
        SELECT
            route,
            departure_date,
            search_date,
            days_before_event,
            price_total,
            airline_code,
            stops
        FROM silver.flight_prices_clean
        WHERE price_total IS NOT NULL
          AND days_before_event IN (90, 30, 10, 1)
        ORDER BY route, days_before_event DESC
    """
    return pd.read_sql(query, engine)


# ─────────────────────────────────────────────
# 2. BOOKING WINDOW MAPPING
# ─────────────────────────────────────────────

BOOKING_WINDOW_MAP = {
    90: "2026-03-13",
    30: "2026-05-12",
    10: "2026-06-01",
    1:  "2026-06-10",
}

WINDOW_LABELS = {
    90: "3 months out",
    30: "1 month out",
    10: "10 days out",
    1:  "Last minute",
}


def map_booking_windows(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["window_label"] = df["days_before_event"].map(WINDOW_LABELS)
    df["search_date_mapped"] = df["days_before_event"].map(BOOKING_WINDOW_MAP)
    # Confirm each snapshot belongs to a valid window
    df = df[df["days_before_event"].isin([90, 30, 10, 1])].reset_index(drop=True)
    return df


# ─────────────────────────────────────────────
# 3. FEATURE ENGINEERING
# ─────────────────────────────────────────────

def engineer_features(df: pd.DataFrame):
    df = df.copy()

    # Encode categoricals
    le_route   = LabelEncoder()
    le_airline = LabelEncoder()

    df["route_enc"]   = le_route.fit_transform(df["route"])
    df["airline_enc"] = le_airline.fit_transform(df["airline_code"])

    # Booking urgency: higher = more urgent (inverse of days_before)
    df["urgency"] = 1 / df["days_before_event"]

    # Route-level aggregates as context features
    route_stats = (
        df.groupby("route")["price_total"]
        .agg(route_avg="mean", route_std="std", route_min="min", route_max="max")
        .reset_index()
    )
    df = df.merge(route_stats, on="route", how="left")
    df["route_std"] = df["route_std"].fillna(0)

    FEATURES = [
        "route_enc",
        "airline_enc",
        "days_before_event",
        "urgency",
        "stops",
        "route_avg",
        "route_std",
        "route_min",
        "route_max",
    ]

    return df, FEATURES, le_route, le_airline


# ─────────────────────────────────────────────
# 4. MODEL TRAINING
# ─────────────────────────────────────────────

def train_model(df: pd.DataFrame, features: list):
    X = df[features]
    y = df["price_total"]

    model = xgb.XGBRegressor(
        n_estimators=200,
        max_depth=4,
        learning_rate=0.05,
        subsample=0.8,
        colsample_bytree=0.8,
        random_state=42,
        verbosity=0,
    )

    # Cross-validated MAE for honest evaluation
    cv_mae = -cross_val_score(model, X, y, cv=3, scoring="neg_mean_absolute_error")
    print(f"\n[Model] Cross-validated MAE: ${cv_mae.mean():.2f} ± ${cv_mae.std():.2f}")

    model.fit(X, y)

    y_pred = model.predict(X)
    print(f"[Model] Train MAE:  ${mean_absolute_error(y, y_pred):.2f}")
    print(f"[Model] Train R²:   {r2_score(y, y_pred):.3f}")

    return model


# ─────────────────────────────────────────────
# 5. PREDICTION LAYER
# ─────────────────────────────────────────────

def generate_predictions(df: pd.DataFrame, model, features: list) -> pd.DataFrame:
    """
    Generate predicted prices for every (route, days_before_event, airline) combo.
    We predict on actual observed rows — not synthetic combinations —
    to stay honest about data coverage.
    """
    df = df.copy()
    df["predicted_price"] = model.predict(df[features]).round(2)
    return df


def route_window_table(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate: avg predicted price per route × booking window."""
    tbl = (
        df.groupby(["route", "days_before_event", "window_label"])
        .agg(
            avg_predicted=("predicted_price", "mean"),
            avg_actual=("price_total", "mean"),
            n_obs=("predicted_price", "count"),
        )
        .reset_index()
        .sort_values(["route", "days_before_event"], ascending=[True, False])
    )
    tbl["avg_predicted"] = tbl["avg_predicted"].round(2)
    tbl["avg_actual"]    = tbl["avg_actual"].round(2)
    return tbl


def route_window_airline_table(df: pd.DataFrame) -> pd.DataFrame:
    """Detailed: avg predicted price per route × window × airline."""
    tbl = (
        df.groupby(["route", "days_before_event", "window_label", "airline_code"])
        .agg(
            avg_predicted=("predicted_price", "mean"),
            avg_actual=("price_total", "mean"),
            n_obs=("predicted_price", "count"),
        )
        .reset_index()
        .sort_values(["route", "days_before_event", "avg_predicted"])
    )
    tbl["avg_predicted"] = tbl["avg_predicted"].round(2)
    tbl["avg_actual"]    = tbl["avg_actual"].round(2)
    return tbl


# ─────────────────────────────────────────────
# 6. RECOMMENDATION LOGIC
# ─────────────────────────────────────────────

EARLY_THRESHOLD  = 0.90   # best window ≤ 90% of overall avg → save significantly booking early
LATE_THRESHOLD   = 1.10   # price at 1-day window > 110% of min → avoid last-minute

def classify_booking_strategy(row: dict) -> str:
    best_days  = row["best_window_days"]
    price_1day = row["price_1day"]
    price_best = row["best_price"]
    price_avg  = row["avg_price_all_windows"]

    if best_days == 1:
        return "Last-minute deals available — monitor prices"
    if best_days >= 90 and price_best < price_avg * EARLY_THRESHOLD:
        return "Book early — prices rise significantly closer to the event"
    if best_days == 30:
        return "Book ~30 days out for best value"
    if best_days == 10:
        return "Book ~10 days out — moderate savings vs early booking"
    if price_1day > price_best * LATE_THRESHOLD:
        return "Avoid last-minute — prices spike near the event"
    return "Prices are relatively stable — book when ready"


def build_recommendation_table(
    rw: pd.DataFrame,          # route × window summary
    rwa: pd.DataFrame,         # route × window × airline detail
) -> pd.DataFrame:
    rows = []

    for route, grp in rw.groupby("route"):
        # Best window = lowest predicted price
        best_idx     = grp["avg_predicted"].idxmin()
        best_row     = grp.loc[best_idx]
        best_days    = int(best_row["days_before_event"])
        best_price   = best_row["avg_predicted"]
        best_label   = best_row["window_label"]

        # Price at 1-day window
        one_day_row  = grp[grp["days_before_event"] == 1]
        price_1day   = one_day_row["avg_predicted"].values[0] if len(one_day_row) > 0 else np.nan

        # Price at 90-day window
        ninety_row   = grp[grp["days_before_event"] == 90]
        price_90     = ninety_row["avg_predicted"].values[0] if len(ninety_row) > 0 else np.nan

        avg_all      = grp["avg_predicted"].mean()
        price_range  = grp["avg_predicted"].max() - grp["avg_predicted"].min()

        # Airlines at best window
        airlines_at_best = rwa[
            (rwa["route"] == route) & (rwa["days_before_event"] == best_days)
        ].sort_values("avg_predicted")

        cheapest_airline  = airlines_at_best.iloc[0]["airline_code"] if len(airlines_at_best) > 0 else "N/A"
        cheapest_price    = airlines_at_best.iloc[0]["avg_predicted"] if len(airlines_at_best) > 0 else np.nan
        priciest_airline  = airlines_at_best.iloc[-1]["airline_code"] if len(airlines_at_best) > 0 else "N/A"
        priciest_price    = airlines_at_best.iloc[-1]["avg_predicted"] if len(airlines_at_best) > 0 else np.nan

        meta = {
            "route": route,
            "best_window_days": best_days,
            "best_window_label": best_label,
            "best_price": best_price,
            "price_90day": price_90,
            "price_1day": price_1day,
            "avg_price_all_windows": avg_all,
            "price_range_usd": price_range,
            "cheapest_airline": cheapest_airline,
            "cheapest_airline_price": cheapest_price,
            "most_expensive_airline": priciest_airline,
            "most_expensive_airline_price": priciest_price,
        }

        meta["recommendation"] = classify_booking_strategy(meta)
        rows.append(meta)

    rec = pd.DataFrame(rows)
    rec["savings_vs_lastminute"] = (rec["price_1day"] - rec["best_price"]).round(2)
    rec["savings_vs_early"]      = (rec["price_90day"] - rec["best_price"]).round(2)
    return rec


# ─────────────────────────────────────────────
# 7. AVIATION-STYLE CONSOLE OUTPUT
# ─────────────────────────────────────────────

def print_recommendations(rec: pd.DataFrame):
    print("\n" + "═" * 62)
    print("  WORLD CUP 2026 — AIRFARE INTELLIGENCE REPORT")
    print("═" * 62)

    for _, row in rec.iterrows():
        savings_lm  = f"${row['savings_vs_lastminute']:.0f}" if not np.isnan(row["savings_vs_lastminute"]) else "N/A"
        savings_e   = f"${row['savings_vs_early']:.0f}"      if not np.isnan(row["savings_vs_early"])      else "N/A"

        print(f"\n  Route: {row['route']}")
        print(f"  ──────────────────────────────────────────────")
        print(f"  Recommended booking window : {row['best_window_label']} ({row['best_window_days']}d before)")
        print(f"  Expected price             : ${row['best_price']:.0f}")
        print(f"  Cheapest airline           : {row['cheapest_airline']} (${row['cheapest_airline_price']:.0f})")
        print(f"  Most expensive airline     : {row['most_expensive_airline']} (${row['most_expensive_airline_price']:.0f})")
        print(f"  Savings vs last-minute     : {savings_lm}")
        print(f"  Savings vs 90-day booking  : {savings_e}")
        print(f"  Advice: {row['recommendation']}")

    print("\n" + "═" * 62)


# ─────────────────────────────────────────────
# 8. MAIN PIPELINE
# ─────────────────────────────────────────────

def run_pipeline(save_outputs=True):
    print("[1/7] Connecting to database...")
    engine = get_engine()

    print("[2/7] Pulling airfare data...")
    df_raw = pull_data(engine)
    print(f"      {len(df_raw):,} rows loaded across {df_raw['route'].nunique()} routes")

    print("[3/7] Mapping booking windows...")
    df = map_booking_windows(df_raw)

    print("[4/7] Engineering features...")
    df, features, le_route, le_airline = engineer_features(df)

    print("[5/7] Training XGBoost regression model...")
    model = train_model(df, features)

    print("[6/7] Generating predictions...")
    df_pred = generate_predictions(df, model, features)

    rw  = route_window_table(df_pred)
    rwa = route_window_airline_table(df_pred)
    rec = build_recommendation_table(rw, rwa)

    print("[7/7] Recommendation report:")
    print_recommendations(rec)

    if save_outputs:
        rw.to_csv("predicted_prices_route_window.csv", index=False)
        rwa.to_csv("predicted_prices_route_window_airline.csv", index=False)
        rec.to_csv("recommendations.csv", index=False)
        print("\n[Output] CSVs saved:")
        print("         → predicted_prices_route_window.csv")
        print("         → predicted_prices_route_window_airline.csv")
        print("         → recommendations.csv")

    return df_pred, rw, rwa, rec, model


# ─────────────────────────────────────────────
# DEMO MODE — runs with synthetic data
# ─────────────────────────────────────────────

def generate_synthetic_data() -> pd.DataFrame:
    """
    Synthetic data for local demo / portfolio presentation.
    Mirrors real schema: route, days_before_event, airline_code, stops, price_total.
    """
    np.random.seed(42)
    routes   = ["BOS-MIA", "BOS-DFW", "LAX-NYC", "ORD-PHX", "SEA-ATL", "DEN-LAX"]
    airlines = {"BOS-MIA": ["AA","DL","B6","F9"],
                "BOS-DFW": ["AA","UA","WN"],
                "LAX-NYC": ["DL","AA","B6","UA"],
                "ORD-PHX": ["AA","UA","WN","F9"],
                "SEA-ATL": ["DL","AA","UA"],
                "DEN-LAX": ["UA","WN","F9","B6"]}
    windows  = [90, 30, 10, 1]
    # Base prices per route (realistic domestic + event surge pattern)
    base     = {"BOS-MIA":320,"BOS-DFW":280,"LAX-NYC":350,"ORD-PHX":200,"SEA-ATL":310,"DEN-LAX":180}
    # Surge multiplier as booking window shrinks
    surge    = {90:1.0, 30:1.15, 10:1.40, 1:1.75}
    # Airline cost index (relative to route base)
    airline_mult = {"AA":1.05,"DL":1.10,"UA":1.08,"B6":0.92,"WN":0.88,"F9":0.80}

    rows = []
    for route in routes:
        for days in windows:
            for airline in airlines[route]:
                for _ in range(3):   # 3 observations per cell (snapshot noise)
                    price = (
                        base[route]
                        * surge[days]
                        * airline_mult.get(airline, 1.0)
                        * np.random.uniform(0.92, 1.08)
                    )
                    stops = np.random.choice([0,1], p=[0.6, 0.4])
                    if stops:
                        price *= 0.90   # connecting slightly cheaper
                    rows.append({
                        "route": route,
                        "departure_date": "2026-06-12",
                        "search_date": BOOKING_WINDOW_MAP[days],
                        "days_before_event": days,
                        "price_total": round(price, 2),
                        "airline_code": airline,
                        "stops": stops,
                    })
    return pd.DataFrame(rows)


def run_demo():
    """Run the full pipeline on synthetic data (no DB needed)."""
    print("\n[DEMO MODE] Running on synthetic data...\n")

    df_raw = generate_synthetic_data()
    print(f"[2/7] Generated {len(df_raw):,} synthetic rows across {df_raw['route'].nunique()} routes")

    df = map_booking_windows(df_raw)
    df, features, le_route, le_airline = engineer_features(df)

    print("[5/7] Training XGBoost regression model...")
    model = train_model(df, features)

    df_pred = generate_predictions(df, model, features)
    rw      = route_window_table(df_pred)
    rwa     = route_window_airline_table(df_pred)
    rec     = build_recommendation_table(rw, rwa)

    print_recommendations(rec)

    rw.to_csv("demo_predicted_prices_route_window.csv", index=False)
    rwa.to_csv("demo_predicted_prices_route_window_airline.csv", index=False)
    rec.to_csv("demo_recommendations.csv", index=False)
    print("\n[Demo Output] Saved: demo_predicted_prices_route_window.csv")
    print("              Saved: demo_predicted_prices_route_window_airline.csv")
    print("              Saved: demo_recommendations.csv")

    return df_pred, rw, rwa, rec, model


if __name__ == "__main__":
    import sys
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_pipeline()
