import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import streamlit as st

st.set_page_config(page_title="London Housing", layout="centered")

pg = st.navigation([
    st.Page("pages/briefing.py", title="Market Briefing", icon="📈"),
    st.Page("pages/affordability.py", title="Affordability Calculator", icon="🏠"),
])
pg.run()
