import streamlit as st
import pandas as pd
import sqlalchemy
from AutoClean import AutoClean
import sweetviz

# Page config
st.set_page_config(page_title="SQL Data Cleaner", layout="wide")
st.title("🧼 SQL Server → Clean & Save Data")

# Input fields
server = st.text_input("🔷 SQL Server Name", value="DESKTOP-263B43H")
database = st.text_input("📂 Database Name")
table = st.text_input("📋 Table Name (e.g., dbo.movies)", value="dbo.movies")

# Initialize session state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'cleaned_df' not in st.session_state:
    st.session_state.cleaned_df = None
if 'run_cleaning' not in st.session_state:
    st.session_state.run_cleaning = False

# Load data button
if st.button("🔄 Load Data from SQL Server"):
    try:
        conn_str = f"mssql+pyodbc://@{server}/{database}?trusted_connection=yes&driver=ODBC+Driver+17+for+SQL+Server"
        engine = sqlalchemy.create_engine(conn_str)
        df = pd.read_sql(f"SELECT * FROM {table}", engine)
        st.session_state.df = df
        st.success("✅ Data loaded successfully!")
    except Exception as e:
        st.error(f"❌ Failed to load data: {e}")

# Show original data
if st.session_state.df is not None:
    st.subheader("📊 Original Data")
    st.dataframe(st.session_state.df)

    # Button to trigger cleaning
    if st.button("🧼 Run AutoClean"):
        st.session_state.run_cleaning = True

# Run AutoClean only if button was clicked
if st.session_state.run_cleaning:
    try:
        pipeline = AutoClean(st.session_state.df, mode='auto', verbose=True)
        cleaned_df = pipeline.output[st.session_state.df.columns]
        st.session_state.cleaned_df = cleaned_df
        st.success("✅ AutoClean completed!")
        st.subheader("🧽 Cleaned Data")
        st.dataframe(cleaned_df)

        if hasattr(pipeline, 'log'):
            st.subheader("⚠️ AutoClean Issues Log")
            for k, v in pipeline.log.items():
                st.write(f"🔸 {k}: {v}")
    except Exception as e:
        st.error(f"❌ AutoClean failed: {e}")
    finally:
        st.session_state.run_cleaning = False  # reset trigger

# Show download and push options
if st.session_state.cleaned_df is not None:
    st.download_button("⬇️ Download Cleaned CSV",
                       st.session_state.cleaned_df.to_csv(index=False),
                       "cleaned_data.csv",
                       "text/csv")

    st.subheader("🛠️ Save Cleaned Data Back to SQL Server")
    target_table = st.text_input("📌 New Table Name", value="dbo.cleaned_movies")
    if st.button("🚀 Push Cleaned Data to SQL Server"):
        try:
            st.session_state.cleaned_df.to_sql(name=target_table.split('.')[-1],
                                               con=engine,
                                               schema=target_table.split('.')[0],
                                               if_exists='replace',
                                               index=False)
            st.success(f"✅ Data saved to SQL Server as: {target_table}")
        except Exception as e:
            st.error(f"❌ Failed to save to SQL Server: {e}")


