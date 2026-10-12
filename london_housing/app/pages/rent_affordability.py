import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import pandas as pd
import plotly.express as px
from app.queries import get_district_rents
from app.calculators import max_affordable_rent
from app.geo import load_geojson, with_uppercase_district_key

st.title("Rent Affordability Calculator")
st.caption("See which districts are within your budget based on average monthly rents")

col_link1, col_link2 = st.columns(2)
col_link1.page_link("pages/briefing.py", label="See this month's market briefing", icon="📈")
col_link2.page_link("pages/affordability.py", label="Looking to buy instead?", icon="🏠")

with st.expander("Where this data comes from"):
    st.markdown(
        "Rents are calculated from the ONS Price Index of Private Rents, which tracks "
        "average advertised rents for local authorities in England and Wales, refreshed "
        "monthly. Figures are mean monthly rent in GBP, broken down by bedroom count."
    )

# ── Inputs ────────────────────────────────────────────────────────────────────
BEDROOM_OPTIONS = {
    "All property sizes": 2,
    "1 bedroom": 3,
    "2 bedroom": 4,
    "3 bedroom": 5,
    "4+ bedroom": 6,
}

col1, col2 = st.columns(2)

with col1:
    salary = st.number_input("Annual salary (£)", min_value=0, value=35000, step=1000)

with col2:
    ratio_pct = st.slider("Rent as % of income", min_value=20, max_value=50, value=35)
    bedroom_choice = st.selectbox("Property size", list(BEDROOM_OPTIONS.keys()))

# ── Summary metrics ───────────────────────────────────────────────────────────
monthly_income = salary / 12
budget = max_affordable_rent(monthly_income, ratio=ratio_pct / 100)

st.divider()

m1, m2 = st.columns(2)
m1.metric("Monthly income", f"£{monthly_income:,.0f}", help="Annual salary ÷ 12")
m2.metric("Max affordable rent", f"£{budget:,.0f}/mo", help=f"{ratio_pct}% of monthly income — a standard affordability rule of thumb")

st.divider()

# ── Data ──────────────────────────────────────────────────────────────────────
rows = get_district_rents()

if not rows:
    st.warning("No rent data available.")
    st.stop()

df = pd.DataFrame(rows, columns=[
    "district", "region", "rent_all", "rent_1bed", "rent_2bed", "rent_3bed", "rent_4bed"
])
rent_col_idx = BEDROOM_OPTIONS[bedroom_choice]
df["rent"] = [row[rent_col_idx] for row in rows]
df = df.dropna(subset=["rent"])

df["within_budget"] = df["rent"] <= budget
df["difference"] = budget - df["rent"]

# ── Map ───────────────────────────────────────────────────────────────────────
st.subheader("Rent affordability map")

geojson = load_geojson()

if geojson is None:
    st.info("Boundary data unavailable — showing table only.")
else:
    geojson = with_uppercase_district_key(geojson)

    map_df = df.copy()
    map_df["status"] = map_df["within_budget"].map({True: "Within budget", False: "Over budget"})
    map_df["rent_label"] = map_df["rent"].apply(lambda p: f"£{p:,.0f}/mo")

    fig = px.choropleth_mapbox(
        map_df,
        geojson=geojson,
        locations="district",
        featureidkey="properties.LAD24NM_upper",
        color="status",
        color_discrete_map={"Within budget": "#2ecc71", "Over budget": "#e74c3c"},
        hover_name="district",
        hover_data={
            "district": False,
            "region": True,
            "rent_label": True,
            "status": False,
        },
        labels={
            "rent_label": "Monthly rent",
            "region": "Region",
        },
        mapbox_style="white-bg",
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
st.subheader("Districts by rent affordability")
st.caption(f"{bedroom_choice} — based on the most recent available month")

df_sorted = df.sort_values("rent")

def format_row(row):
    diff = f"+£{row['difference']:,.0f}" if row["within_budget"] else f"-£{abs(row['difference']):,.0f}"
    return pd.Series({
        "": "✅" if row["within_budget"] else "❌",
        "District": row["district"].title(),
        "Region": row["region"],
        "Monthly rent": f"£{row['rent']:,.0f}",
        "vs. budget": diff,
    })

display_df = df_sorted.apply(format_row, axis=1)
st.dataframe(display_df, use_container_width=True, hide_index=True)
