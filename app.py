import pandas as pd
import streamlit as st

st.title("🔍 Project Search Tool")

# Load file directly from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data(url):
    df = pd.read_excel(url, sheet_name="New Portfolio")  # Change sheet name if needed
    return df

df = load_data(file_url)


    st.write("### Columns in file:", df.columns.tolist())

    # Rename columns (Modify if needed)
    df = df.rename(columns={
        "Company Name": "Project Name",
        "Technology Platform": "Technology",
        "Industry": "Domain",
        "Link": "Project Link"
    })

    # Search bar
    search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

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

