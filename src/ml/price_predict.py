import pandas as pd
from sqlalchemy import create_engine

import matplotlib
matplotlib.use("Agg")   # PHẢI đặt trước pyplot

import matplotlib.pyplot as plt
import numpy as np

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



#===============================
# 1. QUICK DATA CHECK  
#===============================
print(df.info())
print(df.isnull().sum())

# Nếu có missing values thì bỏ tạm để train nhanh
df = df.dropna().copy()

# Optional: đảm bảo đúng kiểu dữ liệu ngày
df["departure_date"] = pd.to_datetime(df["departure_date"])
df["search_date"] = pd.to_datetime(df["search_date"])

# =========================
# 2. Define features and target
# =========================
X = df[["days_before_event", "route", "airline_code", "stops"]].copy()
y = df["price_total"].copy()

# =========================
# 3. Encode categorical variables
# =========================
X = pd.get_dummies(X, columns=["route", "airline_code"], drop_first=False)

print("Encoded feature shape:", X.shape)
print(X.head())

# =========================
# 4. Train / test split
# =========================
from sklearn.model_selection import train_test_split

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

print("X_train shape:", X_train.shape)
print("X_test shape:", X_test.shape)

# =========================
# 5. Train XGBoost model
# =========================
from xgboost import XGBRegressor

model = XGBRegressor(
    n_estimators=200,
    max_depth=5,
    learning_rate=0.08,
    subsample=0.8,
    colsample_bytree=0.8,
    random_state=42
)

model.fit(X_train, y_train)

# =========================
# 6. Evaluate model
# =========================
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import numpy as np

y_pred = model.predict(X_test)

mae = mean_absolute_error(y_test, y_pred)
rmse = np.sqrt(mean_squared_error(y_test, y_pred))
r2 = r2_score(y_test, y_pred)

print("\n=== Model Evaluation ===")
print(f"MAE:  {mae:.2f}")
print(f"RMSE: {rmse:.2f}")
print(f"R²:   {r2:.4f}")


# =========================
# 7. Generate a price curve
# Example: BOS-JFK, UA, non-stop
# =========================
import numpy as np
import matplotlib.pyplot as plt

days = np.arange(1, 91)

curve_df = pd.DataFrame({
    "days_before_event": days,
    "route": ["BOS-JFK"] * len(days),
    "airline_code": ["UA"] * len(days),
    "stops": [0] * len(days)
})

curve_X = pd.get_dummies(curve_df, columns=["route", "airline_code"], drop_first=False)

# Align columns with training data
curve_X = curve_X.reindex(columns=X.columns, fill_value=0)

predicted_prices = model.predict(curve_X)

best_day = days[np.argmin(predicted_prices)]
best_price = predicted_prices.min()

print("\n=== Price Curve Insight ===")
print(f"Best day to book: {best_day} days before departure")
print(f"Lowest predicted price: ${best_price:.2f}")

plt.figure(figsize=(10, 5))
plt.plot(days, predicted_prices)
plt.xlabel("Days Before Departure")
plt.ylabel("Predicted Price")
plt.title("Predicted Price Curve")
plt.gca().invert_xaxis()
plt.grid(True)

plt.savefig("price_curve.png", dpi=300, bbox_inches="tight")
plt.close()

print("Chart saved as price_curve.png")

curve_result = pd.DataFrame({
    "days_before_departure": days,
    "predicted_price": predicted_prices
})
#===============================
print(curve_result.sort_values("days_before_departure"))


#===============================
current_price = df['price_total'].iloc[-1]

if current_price > best_price:
    decision = "WAIT"
else:
    decision = "BUY"

print(f"\nRecommendation: {decision}")

