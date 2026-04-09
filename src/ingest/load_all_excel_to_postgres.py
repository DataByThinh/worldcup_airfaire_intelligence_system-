import pandas as pd
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
from sqlalchemy import create_engine


# ==============================
# 1. DATABASE CONNECTION
# ==============================

load_dotenv()

DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")  

connection_string = f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

engine = create_engine(connection_string)

# test connection
with engine.connect() as conn:
    conn.execute(text("SELECT 1"))
    print("✅ Database connection successful")


# ==============================
# 2. FOLDER STORES FILE CSV
# ==============================

folder_path = r"C:\Users\ASUS\OneDrive - University of Connecticut\Desktop\worldcup-airfaire-intelligence\src\ingest\data\bronze"

# Change path name if you store csv files in another folder


# ==============================
# 3. READ ALL CSV FILES
# ==============================

all_data = []

for file in os.listdir(folder_path):

    if file.endswith(".csv") and not file.startswith("~$"):

        path = os.path.join(folder_path, file)

        print(f" Reading file: {path}")

        df = pd.read_csv(path)

        all_data.append(df)


# kiểm tra có file không
if len(all_data) == 0:
    raise ValueError(" No CSV files found in the folder.")


# ==============================
# 4. COMBINE ALL DATA
# ==============================

combined_df = pd.concat(all_data, ignore_index=True)

print(f"✅ Total rows loaded: {len(combined_df)}")


# ==============================
# 5. LOAD INTO POSTGRESQL
# ==============================

combined_df.to_sql(
    name="flight_prices_raw",
    con=engine,
    schema="bronze",
    if_exists="append",
    index=False
)

print("🚀 Data successfully loaded into PostgreSQL!")