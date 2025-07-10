import streamlit as st
import pandas as pd
import sqlalchemy
from AutoClean import AutoClean
import sweetviz
import os

# 🎨 Page Config
st.set_page_config(page_title="Data Cleaning App", layout="wide")

# 🎨 Custom CSS Inspired by Image
st.markdown("""
<style>
body {
    background-color: #fdfcff;
}
h1, h2, h3, h4 {
    font-family: 'Segoe UI', sans-serif;
}
.gradient-title {
    font-size: 3rem;
    font-weight: 800;
    background: -webkit-linear-gradient(#ff512f, #f09819);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.start-button {
    background-color: #4a90e2;
    color: white;
    padding: 0.8rem 1.5rem;
    font-size: 1rem;
    font-weight: bold;
    border-radius: 50px;
    border: none;
    margin-bottom: 1.5rem;
}
.stTextInput>div>div>input {
    padding: 0.6em;
    border-radius: 8px;
    border: 1px solid #ccc;
}
.stButton>button {
    background-color: #f09819;
    color: white;
    font-weight: bold;
    border: none;
    border-radius: 8px;
    padding: 0.6rem 1.2rem;
    margin-top: 10px;
}
.stButton>button:hover {
    background-color: #ff512f;
}
</style>
""", unsafe_allow_html=True)

# 🧹 Header
st.markdown('<div class="gradient-title">🧹 Data Cleaning</div>', unsafe_allow_html=True)
st.markdown('<button class="start-button">Start Now</button>', unsafe_allow_html=True)

# Step 1: SQL connection inputs
st.subheader("📥 Load Data from SQL Server")
server = st.text_input("🔷 SQL Server Name", value="DESKTOP-263B43H")
database = st.text_input("📂 Database Name")
table = st.text_input("📋 Table Name ", value="dbo.TestCustomers")

# Step 2: Load data from SQL
if st.button("🔄 Load Data from SQL Server"):
    try:
        conn_str = f"mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
        engine = sqlalchemy.create_engine(conn_str)
        st.session_state.engine = engine
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        st.session_state.df = df
        st.success("✅ Data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")

# Step 3: Show data and options
if 'df' in st.session_state:
    st.subheader("📊 Original Data")
    st.dataframe(st.session_state.df, use_container_width=True)

    st.subheader("⚙️ Cleaning Configuration")
    mode = st.selectbox("Select Cleaning Mode", ['auto', 'manual'])

    clean_params = {
        'mode': mode,
        'duplicates': 'auto',
        'missing_num': 'auto',
        'missing_categ': 'auto',
        'encode_categ': False,
        'extract_datetime': 'auto',
        'outliers': 'auto',
        'outlier_param': 1.5,
        'logfile': True,
        'verbose': False
    }

    if mode == 'manual':
        clean_params['duplicates'] = st.selectbox("Handle Duplicates", ['auto', True, False])
        clean_params['missing_num'] = st.selectbox("Missing Numerical", ['auto', 'mean', 'median', 'most_frequent', 'delete', False])
        clean_params['missing_categ'] = st.selectbox("Missing Categorical", ['auto', 'most_frequent', 'delete', False])
        clean_params['extract_datetime'] = st.selectbox("Extract DateTime", ['auto', 'D', 'M', 'Y', 'h', 'm', 's', False])
        clean_params['outliers'] = st.selectbox("Handle Outliers", ['auto', 'winz', 'delete', False])
        clean_params['outlier_param'] = st.slider("Outlier Param (IQR Mult)", 0.5, 5.0, 1.5, 0.1)
        clean_params['logfile'] = st.checkbox("Create Log File", True)
        clean_params['verbose'] = st.checkbox("Verbose Output", False)

    # Step 4: Run AutoClean
    if st.button("🧼 Run AutoClean"):
        try:
            pipeline = AutoClean(st.session_state.df, **clean_params)
            cleaned_df = pipeline.output[st.session_state.df.columns]
            st.session_state.cleaned_df = cleaned_df
            st.success("✅ Cleaning complete!")

            st.subheader("🧽 Cleaned Data")
            st.dataframe(cleaned_df, use_container_width=True)

            if hasattr(pipeline, 'log'):
                st.subheader("⚠️ AutoClean Log")
                for k, v in pipeline.log.items():
                    st.write(f"🔸 {k}: {v}")

            st.subheader("📊 Sweetviz Comparison Report")
            report = sweetviz.compare([st.session_state.df, "Original"], [cleaned_df, "Cleaned"])
            report_path = "sweetviz_report.html"
            report.show_html(report_path)

            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
                st.components.v1.html(html_content, height=800, scrolling=True)

            os.remove(report_path)

        except Exception as e:
            st.error(f"❌ Cleaning failed: {e}")

# Step 5: Save / Download
if 'cleaned_df' in st.session_state:
    st.download_button("⬇️ Download Cleaned CSV",
                       st.session_state.cleaned_df.to_csv(index=False),
                       "cleaned_data.csv",
                       "text/csv")

    st.subheader("🛠️ Save Cleaned Data to SQL Server")
    target_table = st.text_input("📌 Target Table Name", value="dbo.cleaned_data")
    if st.button("🚀 Push to SQL Server"):
        try:
            st.session_state.cleaned_df.to_sql(name=target_table.split('.')[-1],
                                               con=st.session_state.engine,
                                               schema=target_table.split('.')[0],
                                               if_exists='replace',
                                               index=False)
            st.success(f"✅ Saved to SQL Server as: {target_table}")
        except Exception as e:
            st.error(f"❌ Failed to save: {e}")
