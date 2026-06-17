import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st
from app.queries import get_top_rising, get_top_falling
from app.briefing_generator import generate_briefing
import pandas as pd 
import plotly.express as px

st.set_page_config(page_title="London Housing Market Briefing", layout="centered")

st.title("London Housing Market Briefing")
st.caption("AI-generated monthly market analysis from UK Land Registry data")

# can modify if your data spans pass these selctions
month = st.selectbox(
    "Select a month",
    [
        "2023-01-01", "2023-02-01", "2023-03-01", "2023-04-01",
        "2023-05-01", "2023-06-01", "2023-07-01", "2023-08-01",
        "2023-09-01", "2023-10-01", "2023-11-01", "2023-12-01"
    ]
)

if st.button("Generate Briefing"):

    with st.spinner("Querying price data..."):
        rising = get_top_rising(month)
        falling = get_top_falling(month)

    if not rising or not falling:
        st.warning("No data available for this month with the current transaction threshold.")
    else:
        # ── Chart ─────────────────────────────────────────
        chart_data = pd.DataFrame({
            "district": [r[0] for r in rising] + [f[0] for f in falling],
            "mom_change_pct": [r[3] for r in rising] + [f[3] for f in falling]
        })

        fig = px.bar(
            chart_data,
            x="district",
            y="mom_change_pct",
            color="mom_change_pct",
            color_continuous_scale=["red", "white", "green"],
            title=f"Month-on-month price change — {month}"
        )
        st.plotly_chart(fig, use_container_width=True)

        # ── Tables ────────────────────────────────────────
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 3 rising")
            for r in rising:
                st.metric(label=f"{r[0]}", value=f"£{r[2]:,.0f}", delta=f"{r[3]}%")

        with col2:
            st.subheader("Top 3 falling")
            for f in falling:
                st.metric(label=f"{f[0]}", value=f"£{f[2]:,.0f}", delta=f"{f[3]}%")

        # ── AI Briefing ───────────────────────────────────
        st.subheader("Market analysis")
        with st.spinner("Generating briefing..."):
            briefing = generate_briefing(month, rising, falling)
        st.write(briefing)