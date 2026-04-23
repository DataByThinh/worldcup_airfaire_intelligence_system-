# ✈️ World Cup 2026 — Airfare Intelligence & Recommendation System

> **Buy now or wait?** A solo-built, end-to-end data system that converts raw flight data into clear booking decisions for FIFA World Cup 2026 travelers.

# 1. Project Overview

🌍 The **FIFA World Cup 2026** — hosted across the United States, Mexico, and Canada, is one of the largest global sporting events, attracting millions of international travelers and creating significant spikes in airfare demand.

This project collects real-world flight pricing data and applies time-series analysis to identify airfare surges and optimal booking windows, helping travelers make smarter booking decisions within **United States**.

## 1.1 Project Goal 
Build a airfare intelligence system that helps soccer fans worldwide book smarter flights to the FIFA World Cup 2026. Specifically, the system aims to:

- Recommendation System — Identify the optimal booking window per route based on historical price patterns
- Price Intelligence — Detect airfare spikes and trend direction (rising / stable / falling) around match dates
- Smarter Travel Decisions — Recommend the best timing and the most affordable airline per route

## 1.2 Business Questions 

- How do airfare prices change across the 90 → 30 → 10 → 1 day booking windows before World Cup matches?
- When is the statistically best time to book flights to each host city?
- Which airlines offer the most consistent value per route?
- How can we translate price data into a clear, actionable recommendation for fans?

---

# 2. System Architecture
<img width="1500" height="1000" alt="image" src="https://github.com/user-attachments/assets/e9706bdc-3422-4433-8b99-3e1fa0b440a3" />


# 3. 🗄️Data Sources

### **Flight Price Data**

- **Primary Source**: Amadeus Flight Offers API  
- **Data Type**: Real-time airfare pricing  
- **Coverage**: Assgined Top Routes    
- **Windows**: D-90 / D-30 / D-10 / D-1  

Schema: `route`, `departure_date`, `search_date`, `price_total`, `airline_code`, `stops`


- `search_timestamp` – time when the flight price was queried
- `search_date` – date of the price search
- `origin` – departure airport code
- `destination` – arrival airport code
- `route` – flight route identifier
- `origin_name`, `destination_name` – airport names
- `origin_country`, `destination_country` – country information
- `airline_code` – airline operating the flight
- `stops` – number of layovers
- `price_total` – total ticket price
- `currency` – price currency
- `departure_date` – flight departure date
- `days_before_departure` – booking lead time
 <img width="10000" height="500" alt="image" src="https://github.com/user-attachments/assets/0677a636-200c-44d4-9c8d-b58e5c82df2a" />

 # 3. System Architecture


