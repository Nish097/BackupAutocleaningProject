
import os
os.environ["PYTORCH_JIT"] = "0"


import streamlit as st
import pandas as pd
from autoclean import AutoClean
import sweetviz
import os

st.set_page_config(page_title="AutoClean + Sweetviz App", layout="wide")
st.title("🧹📊 AutoClean & Sweetviz - Data Cleaning and Profiling App")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Original Data")
    st.dataframe(df)

    # AutoClean Section
    st.subheader("🧼 AutoClean: Automatic Data Cleaning")
    ac = AutoClean(df, mode='silent')
    cleaned_df = ac.output

    st.success("✅ AutoClean completed successfully!")
    st.dataframe(cleaned_df)

    # Download cleaned data
    st.download_button("⬇️ Download Cleaned CSV", cleaned_df.to_csv(index=False), "cleaned_data.csv", "text/csv")

    # Sweetviz Report
    st.subheader("📊 Sweetviz Report: Data Profiling")
    report = sweetviz.analyze([df, "Original Data"])
    report_path = "sweetviz_report.html"
    report.show_html(report_path)

    # Show report in app
    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        st.components.v1.html(html_content, height=800, scrolling=True)

else:
    st.info("Please upload a CSV file to begin.")
