import streamlit as st
import pandas as pd

st.set_page_config(page_title="Dashboard Sales", layout="wide")

@st.cache_data
def load_data():
    df_in = pd.read_parquet("SELL_IN.parquet")
    df_out = pd.read_parquet("SELLOUT.parquet")
    return df_in, df_out

df_in, df_out = load_data()

st.title("Dashboard Sales Regional Solo Raya")
st.write("Data sudah berhasil dimuat.")
st.write("Sell In Preview:", df_in.head())
st.write("Sell Out Preview:", df_out.head())
