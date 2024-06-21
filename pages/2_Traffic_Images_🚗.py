"""
This page does scrape traffic image data from SG Open Data, &
create dashboard to see overview.

User can choose filter date to change the day overview.
"""

import json
import requests

import pandas as pd
import streamlit as st


st.set_page_config(
    page_title="Traffic in Singapore",
    page_icon="🚗",
    layout="wide",
)

df_location_mapping = pd.read_csv("src/camera_location_mapping.csv")
df_location_mapping["camera_id"] = df_location_mapping["camera_id"].astype(str)

def get_traffic_data():
    """Get Traffic Image Data from data.gov.sg"""

    url = "https://api.data.gov.sg/v1/transport/traffic-images"
    response = requests.get(url, timeout=60)
    result = response.json()

    new_list = []

    for image_info in result["items"][0]["cameras"]:
        new_list.append(image_info)
    df_data = pd.DataFrame.from_dict(new_list, orient='columns')
    df_data[["latitude", "longitude"]] = df_data.location.apply(
        lambda x: pd.Series(json.loads(json.dumps(x)))
    )
    df_data[["height", "width", "md5"]] = df_data.image_metadata.apply(
        lambda x: pd.Series(json.loads(json.dumps(x)))
    )
    df_data = df_data.drop(columns=["location", "image_metadata"])
    df_data = df_data.sort_values(by=["camera_id"]).reset_index(drop=True)
    return df_data


st.title("Traffic in Singapore 🚗")

df = get_traffic_data()
df = df.merge(df_location_mapping, left_on='camera_id', right_on='camera_id')

st.write(f"Latest data updated: {df['timestamp'].max().replace('T',' ')}")
if st.button("Update image"):
    st.rerun()

X = 0
for char in "ABCDEFGHIJKLMNO":
    locals()[f'col{char}1'], locals()[f'col{char}2'], locals()[f'col{char}3'] = st.columns(3)
    for i in range(1,4):
        locals()[f'col{char}{i}'].image(
            df["image"][X],
            caption=f"{df['location_name'][X]} ({df['timestamp'].max().replace('T',' ')})",
            use_column_width=True
        )
        X+=1
