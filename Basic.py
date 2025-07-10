import streamlit as st
import pandas as pd


st.set_page_config(page_title="Data Cleaning App", layout="wide")


st.title(" Data Cleaning and Exploration App")


uploaded_file = st.file_uploader("upload your csv file",type=["csv"])


if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.subheader(" Raw data")
    st.write(df.head())
    
    
    
    
    st.subheader("Missing value handler")
    if st.checkbox("Drop rows with missing values"):
        df.dropna(inplace=True)
        st.success("Null rows dropped")
        
        
        
        
    fill_option = st.selectbox("Fill remaining null value with:" , ["None", "Zero", "Mean"]) 
    if fill_option == "Zero":
        df.fillna(0,inplace=True)
    elif fill_option == "Mean":
         df.fillna(df.mean(numeric_only=True), inplace=True)    
         
         
         
    st.subheader("Convert column data type")
    col = st.selectbox("Choose columns", df.columns)
    dtype = st.selectbox("Convert to type",["int","float","str","datetime"])
    if st.button("Convert Type"):
        try:
            if dtype == "datetime":
                df[col] = pd.to_datetime(df[col])
            else:
                df[col] = df[col].astype(dtype)
            st.success(f"{col} converted to {dtype}")
        except Exception as e:
            st.error(f"Error: {e}")
                       
       
       
        
        
        
    if st.button("Drop duplicates"):
        df.drop_duplicates(inplace=True)
        st.success("Duplicates removed.")
        
        
           
    
    st.subheader("Download Cleanes file")
    st.download_button("Download CSV", df.to_csv(index=False), "cleaned_data.csv","text/csv")