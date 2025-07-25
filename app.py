import streamlit as st
import pandas as pd
import sqlalchemy
from AutoClean import AutoClean
import os

# Streamlit page config
st.set_page_config(page_title="SQL Auto Data Cleaner", layout="wide")
st.title("🧼 The Data Therapist")

# Inject CSS early
if os.path.exists("style.css"):
    with open("style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Step 1: Data Source Selection
data_source = st.radio("📥 Select Data Source", ["Upload CSV", "Connect to SQL Server"])

# CSV Upload Option
if data_source == "Upload CSV":
    uploaded_file = st.file_uploader("📁 Upload CSV File", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.session_state.df = df
        st.success("✅ CSV file loaded successfully!")

# SQL Server Option
if data_source == "Connect to SQL Server":
    server = st.text_input("🔷 SQL Server Name", value="DESKTOP-263B43H")
    database = st.text_input("📂 Database Name")

    # Show query/table option only after database is entered
    if server and database:
        query_mode = st.radio("📄 Choose how to load data:", ["Use Table Name", "Write SQL Query"])

        if query_mode == "Use Table Name":
            table = st.text_input("📋 Enter Table Name", value="dbo.TestCustomers")
        else:
            custom_query = st.text_area("🧠 Write your SQL Query",
                                        placeholder="SELECT Name, Age FROM dbo.Customers WHERE Age > 25",
                                        height=150)

        if st.button("🔄 Connect and Load Data"):
            try:
                conn_str = f"mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
                engine = sqlalchemy.create_engine(conn_str)
                st.session_state.engine = engine

                if query_mode == "Use Table Name":
                    df = pd.read_sql(f"SELECT * FROM {table}", engine)
                else:
                    df = pd.read_sql(custom_query, engine)

                st.session_state.df = df
                st.success("✅ Data loaded successfully!")

            except Exception as e:
                st.error(f"❌ Failed to load data: {e}")



# Show original data
if 'df' in st.session_state:
    st.subheader("📊 Original Data")
    st.dataframe(st.session_state.df)

    # Step 3: Mode selection
    st.subheader("⚙️ Cleaning Configuration")
    mode = st.selectbox("Select Cleaning Mode", ['auto', 'manual'])

    clean_params = {
        'mode': mode,
        'duplicates': 'auto',
        'missing_num': 'auto',
        'missing_categ': 'auto',
        'encode_categ': 'auto',
        'extract_datetime': 'auto',
        'outliers': 'auto',
        'outlier_param': 1.5,
        'logfile': True,
        'verbose': False
    }

    if mode == 'manual':
        clean_params['duplicates'] = st.selectbox("Handle Duplicates", ['auto', True, False])
        clean_params['missing_num'] = st.selectbox("Missing Numerical", ['auto', 'linreg','mean', 'median', 'most_frequent', 'delete', False])
        clean_params['missing_categ'] = st.selectbox("Missing Categorical", ['auto', 'logreg', 'most_frequent', 'delete', False])
        clean_params['extract_datetime'] = st.selectbox("Extract DateTime", ['auto', 'D', 'M', 'Y', 'h', 'm', 's', False])
        clean_params['outliers'] = st.selectbox("Handle Outliers", ['auto', 'winz', 'delete', False])
        clean_params['outlier_param'] = st.slider("Outlier Param (IQR Mult)", 0.5, 5.0, 1.5, 0.1)
        clean_params['logfile'] = st.checkbox("Create Log File", True)
        clean_params['verbose'] = st.checkbox("Verbose Output", False)

    # Step 4: Run cleaning
    if st.button("🧼 Run AutoClean"):
        try:
            df_cleaning = st.session_state.df.copy()
            for col in df_cleaning.select_dtypes(include=['number']).columns:
                df_cleaning[col] = pd.to_numeric(df_cleaning[col], errors='coerce').astype('float64').round(2)

            pipeline = AutoClean(df_cleaning, **clean_params)
            cleaned_df = pipeline.output[df_cleaning.columns]
            st.session_state.cleaned_df = cleaned_df
            st.success("✅ Cleaning complete!")

            st.subheader("🧽 Cleaned Data")
            st.dataframe(cleaned_df)

            if hasattr(pipeline, 'log'):
                st.subheader("⚠️ AutoClean Log")
                for k, v in pipeline.log.items():
                    st.write(f"🔸 {k}: {v}")

        except Exception as e:
            st.error(f"❌ Cleaning failed: {e}")

# Step 6: Save & Download cleaned data
if 'cleaned_df' in st.session_state:
    st.download_button("⬇️ Download Cleaned CSV",
                       st.session_state.cleaned_df.to_csv(index=False),
                       "cleaned_data.csv",
                       "text/csv")

    if data_source == "Connect to SQL Server":
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
