"""
This page does scrape 1-week data from SG Open Data, &
create dashboard to see day & 1-week overview.

User can choose filter date to change the day overview.
"""

import datetime
import requests


import pandas as pd
import streamlit as st

import plotly.express as px

st.set_page_config(
    page_title="UV Index in Singapore",
    page_icon="🦁",
    layout="wide",
)

TODAY = datetime.date.today()
YESTERDAY = TODAY - datetime.timedelta(days=1)

st.title("UV Index in Singapore 😎")

@st.cache_data
def get_uv_data(date):
    """Get UV Index Data from data.gov.sg"""

    url = f"https://api.data.gov.sg/v1/environment/uv-index?date={date}"
    response = requests.get(url, timeout=60)
    result = response.json()

    new_list = []

    for item in result["items"]:
        for index in item["index"]:
            new_list.append(index)
    df_data = pd.DataFrame.from_dict(new_list, orient='columns')
    df_data = df_data.sort_values(by=["timestamp"]).drop_duplicates().reset_index(drop=True)
    return df_data

# Consume 1-week UVI Data
df_7days = pd.DataFrame()
for i in range(7):
    df = get_uv_data(TODAY - datetime.timedelta(days=i))
    if len(df) == 0:
        df = get_uv_data(TODAY - datetime.timedelta(days=7))
    df_7days = pd.concat([df_7days, df])

# Extract date & time
df_7days["timestamp"] = pd.to_datetime(df_7days["timestamp"])
df_7days["date"] = df_7days["timestamp"].dt.date
df_7days["time"] = df_7days["timestamp"].dt.strftime("%H:%M:%S")

st.write(f"Latest data updated: {df_7days['timestamp'].max()}")

date_selected = st.selectbox("Choose date", df_7days["date"].unique())

df_day_selected = df_7days.loc[df_7days["date"] == date_selected]
df_today = df_7days.loc[df_7days["date"] == TODAY]
df_yesterday = df_7days.loc[df_7days["date"] == YESTERDAY]

# Create Line Chart
st.markdown(
    "<h2 style='text-align: center;'>1 Day Overview of UV Index in Singapore</h2>",
    unsafe_allow_html=True
)
level_list = ["Moderate", "High"]
color_lever_dict = dict([*zip(
    level_list, px.colors.qualitative.Plotly[:len(level_list)]
)])
lowestXAxis = df_day_selected['timestamp'].min() - datetime.timedelta(hours=1)
highestXAxis = df_day_selected['timestamp'].min() + datetime.timedelta(hours=13)
xrange = [lowestXAxis, highestXAxis]
line_chart = px.line(df_day_selected, x='timestamp', y="value")
line_chart.update_xaxes(range=xrange)
for level in level_list:
    Y = 3 if level == "Moderate" else 7
    line_chart.add_hline(
        y=Y, line_width=1, line_dash="dash",
        line_color=color_lever_dict[level]
    )
    line_chart.add_annotation(
        x=df_day_selected["timestamp"][0], y=Y,
        text=level,
        showarrow=False,
        yshift=12
    )
if date_selected == TODAY:
    line_chart.add_vline(
        x=df_day_selected['timestamp'].max(), line_width=1, line_dash="dash",
        line_color=color_lever_dict["Moderate"]
    )
    max_timestamp = df_day_selected['timestamp'].max()
    line_chart.add_annotation(
        x=max_timestamp + datetime.timedelta(minutes=35),
        y=df_day_selected[df_day_selected['timestamp'] == max_timestamp]['value'].iloc[0]+0.3,
        text="Last data updated",
        showarrow=False,
    )
line_chart.update_layout(
    yaxis_title="UV Index",
    xaxis_title="Timestamp",
)
st.plotly_chart(line_chart)


# Create Bar Chart
st.markdown(
    "<h2 style='text-align: center;'>Week Overview of UV Index in Singapore (Average)</h2>",
    unsafe_allow_html=True
)
df_mean = df_7days.groupby("date").mean("value").reset_index()
bar_chart = px.bar(df_mean, x='date', y='value', text_auto='.2s')
bar_chart.update_traces(textfont_size=16, textangle=0, textposition="outside", cliponaxis=False)
bar_chart.update_layout(
    yaxis_title="Average of UV Index",
    xaxis_title="Date",
)
st.plotly_chart(bar_chart)


# Create Insight
today_avg = df_today["value"].mean()
yesterday_avg = df_yesterday["value"].mean()
if today_avg > yesterday_avg:
    COMPARATION = "higher"
elif today_avg < yesterday_avg:
    COMPARATION = "lower"
else:
    COMPARATION = "equal"
if df_today['timestamp'].max() != df_today['timestamp'].min() + datetime.timedelta(hours=12):
    CONTRA = "But, today's UV Index Data is not completed yet, please wait until 6pm."
else:
    CONTRA = ""
st.markdown(
    f"<p>Insight: Today's average of UV Index is <b>{COMPARATION}</b> than yesterday. {CONTRA}</p>",
    unsafe_allow_html=True
)
