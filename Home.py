"""Homepage of SG Open Data Exploration"""

import streamlit as st


st.set_page_config(
    page_title="SG Open Data Exploration",
    page_icon="🦁",
    layout="wide",
)

st.title("SG Open Data Exploration")
st.markdown(
    "Welcome to the **Singapore Open Data Explorer** repository! This project leverages data " +
    "from the [Singapore Open Data](https://data.gov.sg) platform to build interactive " +
    "dashboards and other data visualizations using Streamlit. The goal is to make data " +
    "exploration accessible and insightful for everyone interested in Singapore's diverse datasets."
)
