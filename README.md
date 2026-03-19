# World Cup 2026 Airfare Intelligence & Recommendation System

# 1. Project Overview
⚠️ Planning to watch the World Cup live? 
— Airfare prices may spike before kickoff 

🌍 The **FIFA World Cup 2026** — hosted across the United States, Mexico, and Canada, is one of the largest global sporting events, attracting millions of international travelers and creating significant spikes in airfare demand.

This project collects real-world flight pricing data and applies time-series analysis to identify airfare surges and optimal booking windows, helping travelers make smarter booking decisions. 

## 1.1 Project Goal 
🎯 The goal of this project is to use airfare data to generate insights that help travelers make smarter booking decisions during the FIFA World Cup 2026. Specifically, the system aims to:

- **Recommendation System**: Build a data-driven airfare recommendation system that helps soccer fans worldwide book smarter flights for the FIFA World Cup 2026
- **Price Intelligence**: Identify airfare spikes and booking patterns around World Cup matches
- **Smarter Travel Decisions**: Recommend optimal booking windows and alternative routes.

## 1.2 Business Questions 
- How do airfare prices change before and during the FIFA World Cup?
- Which routes experience the largest price increases?
- When is the best time to book flights?
- How can we recommend smarter travel options for soccer fans?

# 2. Data Sources
### **Flight Price Data**
🗄️ Real-world airfare data collected via the **Amadeus Flight Offers API**, including: 

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
