import pandas as pd
import streamlit as st

# Load the file directly from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")  # Change sheet name if needed

df = load_data()

st.title("🔍 Project Search Tool")

# Show available columns
st.write("### Columns in file:", df.columns.tolist())

# Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# Filtering logic
if search_query:
    keywords = [kw.strip().lower() for kw in search_query.split(",")]
    filtered_df = df[df.apply(lambda row: any(kw in str(row.values).lower() for kw in keywords), axis=1)]

    if not filtered_df.empty:
        st.write(f"### Found {len(filtered_df)} matching projects:")
        st.dataframe(filtered_df)
    else:
        st.warning("No projects found matching your search.")
else:
    st.info("Enter a keyword to begin your search.")
