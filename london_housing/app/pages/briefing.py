import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import streamlit as st
import duckdb
import pandas as pd
import plotly.express as px
from app.queries import get_top_rising, get_top_falling, DB_PATH
from app.briefing_generator import generate_briefing


@st.cache_data(ttl=3600)
def get_available_months():
    con = duckdb.connect(DB_PATH, read_only=True)
    rows = con.execute("""
        SELECT DISTINCT strftime(transfer_month, '%Y-%m-%d')
        FROM fct_price_index
        ORDER BY 1 DESC
    """).fetchall()
    con.close()
    return [r[0] for r in rows]


st.title("Market Briefing")
st.caption("AI-generated monthly analysis from UK Land Registry data")

st.page_link("pages/affordability.py", label="Can you afford to buy in these areas?", icon="🏠")

with st.expander("Where this data comes from"):
    st.markdown(
        "Every month's briefing is generated from HM Land Registry's official "
        "record of residential property sales. It ranks districts by month-on-"
        "month price change, then an AI model writes a short, factual summary of "
        "what moved and why it might have — districts with fewer than 20 sales "
        "that month are excluded so the ranking isn't skewed by a handful of deals."
    )

months = get_available_months()
month = st.selectbox("Select a month", months)

if st.button("Generate Briefing"):

    with st.spinner("Querying price data..."):
        rising = get_top_rising(month)
        falling = get_top_falling(month)

    if not rising or not falling:
        st.warning("No data available for this month with the current transaction threshold.")
    else:
        chart_data = pd.DataFrame({
            "district": [r[0].title() for r in rising] + [f[0].title() for f in falling],
            "mom_change_pct": [r[3] for r in rising] + [f[3] for f in falling]
        })

        fig = px.bar(
            chart_data,
            x="district",
            y="mom_change_pct",
            color="mom_change_pct",
            color_continuous_scale=["red", "white", "green"],
            labels={"district": "District", "mom_change_pct": "Price change vs. last month"},
            title=f"Month-on-month price change — {month}"
        )
        fig.update_yaxes(ticksuffix="%")
        fig.update_coloraxes(colorbar_ticksuffix="%")
        st.plotly_chart(fig, use_container_width=True)

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top 3 rising")
            for r in rising:
                st.metric(label=r[0].title(), value=f"£{r[2]:,.0f}", delta=f"{r[3]}%")

        with col2:
            st.subheader("Top 3 falling")
            for f in falling:
                st.metric(label=f[0].title(), value=f"£{f[2]:,.0f}", delta=f"{f[3]}%")

        st.subheader("Market analysis")
        with st.spinner("Generating briefing..."):
            briefing = generate_briefing(month, rising, falling)
        st.write(briefing)
