# AutoCleaning_Project
#  SQL Auto Data Cleaner using Streamlit + AutoClean

This project is Streamlit web app that connects to a SQL Server database, loads a selected table, and automatically cleans the data using the **AutoClean** library. It also allows exporting cleaned data as CSV or saving it back to the SQL Server.

---

## 🔧 Features

- 🔌 Connect to any **SQL Server** (using server name, DB name, table name)
- 📊 Preview **original raw data**
- ⚙️ Configure and apply **data cleaning**
  - Remove duplicates
  - Handle missing values
  - Encode categorical variables
  - Handle outliers
  - Extract datetime components
- 🧽 See the **cleaned data**
- 💾 Download cleaned data as CSV
- 🚀 Save cleaned data back to SQL Server

---

## 🚀 How It Works

1. 🖥️ **Streamlit app runs locally** (`localhost:8501`)
2. 🛢️ Connects to **SQL Server** using connection string
3. 📥 Loads the selected SQL table into a **Pandas DataFrame**
4. 🧼 Cleans the data using the **AutoClean pipeline**
5. 📤 Allows download or saving back to SQL Server

---

