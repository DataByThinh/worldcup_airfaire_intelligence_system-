import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="World Cup Airfare Intelligence", layout="wide")

st.title("World Cup Airfare Intelligence System")
st.caption("Booking window and airline recommendation by route")

# Load data
presentation_path = "outputs/presentation_table.csv"
route_stats_path = "outputs/route_window_stats.csv"
airline_stats_path = "outputs/airline_window_stats.csv"

presentation_df = pd.read_csv(presentation_path)
route_stats_df = pd.read_csv(route_stats_path)
airline_stats_df = pd.read_csv(airline_stats_path)

# Sidebar
st.sidebar.header("Filters")

routes = sorted(presentation_df["route"].dropna().unique())
selected_route = st.sidebar.selectbox("Select Route", routes)

# Filter route-level summary
route_summary = presentation_df[presentation_df["route"] == selected_route].copy()

if route_summary.empty:
    st.warning("No data available for this route.")
    st.stop()

best_window = route_summary["best_booking_window"].iloc[0]
best_days = route_summary["best_days_before_event"].iloc[0]
cheapest_airline = route_summary["cheapest_airline"].iloc[0]
cheapest_price = route_summary["cheapest_avg_price"].iloc[0]
most_expensive_airline = route_summary["most_expensive_airline"].iloc[0]
most_expensive_price = route_summary["most_expensive_avg_price"].iloc[0]

# Top recommendation cards
col1, col2, col3, col4 = st.columns(4)

col1.metric("Best Booking Window", f"{best_window}")
col2.metric("Cheapest Airline", f"{cheapest_airline}", f"${cheapest_price:,.2f}")
col3.metric("Most Expensive Airline", f"{most_expensive_airline}", f"${most_expensive_price:,.2f}")
col4.metric("Price Gap", f"${(most_expensive_price - cheapest_price):,.2f}")

st.divider()

# Route-level booking window chart
st.subheader(f"Booking Window Trend: {selected_route}")

route_chart_df = route_stats_df[route_stats_df["route"] == selected_route].copy()
route_chart_df = route_chart_df.sort_values("booking_window_days", ascending=False)

if not route_chart_df.empty:
    chart_df = route_chart_df[["booking_window_days", "avg_price"]].copy()
    chart_df["booking_window_days"] = chart_df["booking_window_days"].astype(str)
    st.line_chart(chart_df.set_index("booking_window_days"))
else:
    st.info("No booking window trend data available.")

st.divider()

# Airline comparison inside best window
st.subheader(f"Airline Comparison in Recommended Window ({best_window})")

airline_chart_df = airline_stats_df[
    (airline_stats_df["route"] == selected_route) &
    (airline_stats_df["booking_window"] == best_window)
].copy()

if not airline_chart_df.empty:
    airline_chart_df = airline_chart_df.sort_values("avg_price", ascending=True)
    st.bar_chart(
        airline_chart_df.set_index("airline_code")["avg_price"]
    )
    st.dataframe(
        airline_chart_df[["airline_code", "avg_price", "median_price", "offer_count"]],
        use_container_width=True
    )
else:
    st.info("No airline comparison data available for this route and window.")

st.divider()

# Final summary table
st.subheader("Route Recommendation Summary")
st.dataframe(route_summary, use_container_width=True)