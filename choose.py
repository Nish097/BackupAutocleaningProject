import streamlit as st
import pandas as pd
from AutoClean import AutoClean
import sweetviz
import os

st.set_page_config(page_title="Smart Data Cleaner", layout="wide")
st.title("🧹 Automatic Data Cleaner App")

uploaded_file = st.file_uploader("📤 Upload your CSV file", type=["csv"])

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.subheader("🔍 Original Data")
    st.dataframe(df)

    st.subheader("⚙️ Select Cleaning Mode")
    mode = st.selectbox("Choose Mode", ['auto', 'manual'])

    # Default values for all parameters
    duplicates = 'auto'
    missing_num = 'auto'
    missing_categ = 'auto'
    encode_categ = 'auto'
    extract_datetime = 'auto'
    outliers = 'auto'
    outlier_param = 1.5
    logfile = True
    verbose = False

    # If manual, let user control parameters
    if mode == 'manual':
        st.markdown("### 🔧 Manual Cleaning Options")

        duplicates = st.selectbox("Handle Duplicates", ['auto', True, False])
        missing_num = st.selectbox("Handle Missing Numerical", 
                                   ['auto', 'linreg', 'knn', 'mean', 'median', 'most_frequent', 'delete', False])
        missing_categ = st.selectbox("Handle Missing Categorical", 
                                     ['auto', 'logreg', 'knn', 'most_frequent', 'delete', False])
        encode_categ = st.selectbox("Encode Categorical Variables", 
                                    ['auto', ['onehot'], ['label'], False])
        extract_datetime = st.selectbox("Extract DateTime Features", 
                                        ['auto', 'D', 'M', 'Y', 'h', 'm', 's', False])
        outliers = st.selectbox("Handle Outliers", ['auto', 'winz', 'delete', False])
        outlier_param = st.slider("Outlier Parameter (IQR Multiplier)", 0.5, 5.0, 1.5, step=0.1)
        logfile = st.checkbox("Create Log File", value=True)
        verbose = st.checkbox("Verbose Output", value=False)

    # Clean Data button
    if st.button("🧼 Clean Data"):
        st.subheader("🚀 Running AutoClean...")
        try:
            pipeline = AutoClean(df,
                                 mode=mode,
                                 duplicates=duplicates,
                                 missing_num=missing_num,
                                 missing_categ=missing_categ,
                                 encode_categ=encode_categ,
                                 extract_datetime=extract_datetime,
                                 outliers=outliers,
                                 outlier_param=outlier_param,
                                 logfile=logfile,
                                 verbose=verbose)

            cleaned_df = pipeline.output[df.columns]
            st.success("✅ AutoClean completed!")

            st.subheader("🧽 Cleaned Data")
            st.dataframe(cleaned_df)

            if hasattr(pipeline, 'log'):
                st.subheader("⚠️ Issues AutoClean Couldn't Fix")
                for k, v in pipeline.log.items():
                    st.write(f"🔸 {k}: {v}")

            st.download_button("⬇️ Download Cleaned CSV",
                               cleaned_df.to_csv(index=False),
                               "cleaned_data.csv",
                               "text/csv")

            st.subheader("📊 Sweetviz Report")
            report = sweetviz.analyze([df, "Original Data"])
            report_path = "sweetviz_report.html"
            report.show_html(report_path)
                        
                        
            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=800, scrolling=True)
            
            
            st.subheader("📊 Sweetviz Report2")
            report2 = sweetviz.analyze([cleaned_df, "Cleaned Original Data"])
            report_path2 = "sweetviz_report2.html"
            report2.show_html(report_path2)

            with open(report_path2, 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=800, scrolling=True)

            os.remove(report_path)

        except Exception as e:
            st.error(f"❌ Error during cleaning: {e}")

else:
    st.info("📁 Please upload a CSV file to begin.")
