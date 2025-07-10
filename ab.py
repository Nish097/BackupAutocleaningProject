import streamlit as st
import pandas as pd
from AutoClean import AutoClean
import sweetviz
import os

st.set_page_config(page_title="Smart Data Cleaner", layout="wide")
st.title("Automatic Data Cleaner")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Original Data")
    st.dataframe(df)
    
   ## Add options selected by user and button for action

    st.subheader("🧼 Cleaning Data with AutoClean...")
    pipeline = AutoClean(df, mode='auto', verbose=True)

    cleaned_df = pipeline.output[df.columns]
    st.success("✅ AutoClean completed!")
    st.subheader("🧽 Cleaned Data")
    st.dataframe(cleaned_df)

    ##error handling optimise 
    # Show uncleaned info
    if hasattr(pipeline, 'log'):
        st.subheader("⚠️ Issues AutoClean Couldn't Fix")
        for k, v in pipeline.log.items():
            st.write(f"🔸 {k}: {v}")

    # Download button
    st.download_button("⬇️ Download Cleaned CSV", cleaned_df.to_csv(index=False), "cleaned_data.csv", "text/csv")

    ## 2 reports
    # Sweetviz profiling
    st.subheader("📊 Sweetviz Report")
    report = sweetviz.analyze([df, "Original Data"])
    report_path = "sweetviz_report.html"
    report.show_html(report_path)

    with open(report_path, 'r', encoding='utf-8') as f:
        html_content = f.read()
        st.components.v1.html(html_content, height=800, scrolling=True)

else:
    st.info(" Please upload a CSV file to begin.")

