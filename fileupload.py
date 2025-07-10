import streamlit as st
import pandas as pd

st.set_page_config(page_title="Simple Test App", layout="wide")
st.title("🚀 Data Cleaning App")

# File uploader widget
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Conditional display
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.success("File uploaded successfully!")
    st.write("### Preview of your data:")
    st.dataframe(df)
else:
    st.info("Please upload a CSV file to get started.")



