import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import json
import requests
import streamlit as st
import pandas as pd
import plotly.express as px
from app.queries import get_district_prices

# ONS Local Authority Districts boundary GeoJSON (simplified, public domain)
# BGC = Boundaries Generalised Clipped — lower resolution, faster to load
GEOJSON_URL = (
    "https://services1.arcgis.com/ESMARspQHYMw9BZ9/arcgis/rest/services/"
    "Local_Authority_Districts_May_2024_Boundaries_UK_BGC/FeatureServer/0/query"
    "?where=1%3D1&outFields=LAD24NM&f=geojson&returnGeometry=true"
)
GEOJSON_CACHE = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "districts.geojson"
)


@st.cache_data(ttl=86400 * 30)
def load_geojson():
    if os.path.exists(GEOJSON_CACHE):
        with open(GEOJSON_CACHE) as f:
            return json.load(f)
    try:
        resp = requests.get(GEOJSON_URL, timeout=30)
        resp.raise_for_status()
        data = resp.json()
        os.makedirs(os.path.dirname(GEOJSON_CACHE), exist_ok=True)
        with open(GEOJSON_CACHE, "w") as f:
            json.dump(data, f)
        return data
    except Exception:
        return None


def monthly_repayment(principal: float, annual_rate: float, term_years: int) -> float:
    r = annual_rate / 100 / 12
    n = term_years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


st.title("Affordability Calculator")
st.caption("See which districts are within your budget based on average sale prices")

# ── Inputs ────────────────────────────────────────────────────────────────────
col1, col2 = st.columns(2)

with col1:
    salary = st.number_input("Annual salary (£)", min_value=0, value=50000, step=1000)
    deposit = st.number_input("Deposit (£)", min_value=0, value=30000, step=1000)

with col2:
    term = st.slider("Mortgage term (years)", min_value=10, max_value=35, value=25)
    rate = st.number_input("Interest rate (%)", min_value=0.1, max_value=20.0, value=4.5, step=0.1)

# ── Summary metrics ───────────────────────────────────────────────────────────
INCOME_MULTIPLE = 4.5
max_loan = salary * INCOME_MULTIPLE
total_budget = max_loan + deposit
monthly_payment = monthly_repayment(max_loan, rate, term)

st.divider()

m1, m2, m3 = st.columns(3)
m1.metric("Max loan", f"£{max_loan:,.0f}", help=f"Based on {INCOME_MULTIPLE}x salary — standard lender maximum")
m2.metric("Total budget", f"£{total_budget:,.0f}", help="Max loan + deposit")
m3.metric("Monthly repayment", f"£{monthly_payment:,.0f}", help="On the maximum loan at the given rate and term")

st.divider()

# ── Data ──────────────────────────────────────────────────────────────────────
rows = get_district_prices()

if not rows:
    st.warning("No price data available.")
    st.stop()

df = pd.DataFrame(rows, columns=["district", "county", "avg_price", "median_price", "transactions"])
df["within_budget"] = df["avg_price"] <= total_budget
df["difference"] = total_budget - df["avg_price"]
df["monthly_repayment"] = df["avg_price"].apply(
    lambda p: monthly_repayment(max(p - deposit, 0), rate, term)
)
df["district_upper"] = df["district"].str.upper()

# ── Map ───────────────────────────────────────────────────────────────────────
st.subheader("Affordability map")

geojson = load_geojson()

if geojson is None:
    st.info("Boundary data unavailable — showing table only.")
else:
    # normalise GeoJSON district names to uppercase for matching
    for feature in geojson["features"]:
        name = feature["properties"].get("LAD24NM", "")
        feature["properties"]["LAD24NM_upper"] = name.upper()

    map_df = df.copy()
    map_df["status"] = map_df["within_budget"].map({True: "Within budget", False: "Over budget"})
    map_df["avg_price_label"] = map_df["avg_price"].apply(lambda p: f"£{p:,.0f}")
    map_df["repayment_label"] = map_df["monthly_repayment"].apply(lambda p: f"£{p:,.0f}/mo")

    fig = px.choropleth_mapbox(
        map_df,
        geojson=geojson,
        locations="district_upper",
        featureidkey="properties.LAD24NM_upper",
        color="status",
        color_discrete_map={"Within budget": "#2ecc71", "Over budget": "#e74c3c"},
        hover_name="district",
        hover_data={
            "district_upper": False,
            "county": True,
            "avg_price_label": True,
            "repayment_label": True,
            "status": False,
        },
        labels={
            "avg_price_label": "Avg price",
            "repayment_label": "Monthly repayment",
            "county": "County",
        },
        mapbox_style="carto-positron",
        center={"lat": 52.5, "lon": -1.5},
        zoom=5.2,
        opacity=0.7,
        height=550,
    )
    fig.update_layout(margin={"r": 0, "t": 0, "l": 0, "b": 0}, legend_title_text="")
    st.plotly_chart(fig, use_container_width=True)

    affordable = df["within_budget"].sum()
    total = len(df)
    st.caption(f"{affordable} of {total} districts within your budget")

# ── Table ─────────────────────────────────────────────────────────────────────
st.subheader("Districts by affordability")
st.caption("Based on average sale prices in the most recent available month")

df_sorted = df.sort_values("avg_price")

def format_row(row):
    diff = f"+£{row['difference']:,.0f}" if row["within_budget"] else f"-£{abs(row['difference']):,.0f}"
    return pd.Series({
        "": "✅" if row["within_budget"] else "❌",
        "District": row["district"],
        "County": row["county"],
        "Avg price": f"£{row['avg_price']:,.0f}",
        "Median price": f"£{row['median_price']:,.0f}",
        "vs. budget": diff,
        "Monthly repayment": f"£{row['monthly_repayment']:,.0f}",
        "Transactions": int(row["transactions"]),
    })

display_df = df_sorted.apply(format_row, axis=1)
st.dataframe(display_df, use_container_width=True, hide_index=True)
