import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup  
import requests  

# Load the file directly from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")  

df = load_data()

st.title("🔍 Project Search Tool")

# **Debugging Step: Print Available Columns**
st.write("### Available Columns:", df.columns.tolist())

# Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

filtered_df = pd.DataFrame()  

if search_query:
    query = search_query.strip().lower()

    if " and " in query:
        keywords = query.split(" and ")
        filtered_df = df[df.apply(lambda row: all(kw in str(row.values).lower() for kw in keywords), axis=1)]
    elif " or " in query:
        keywords = query.split(" or ")
        filtered_df = df[df.apply(lambda row: any(kw in str(row.values).lower() for kw in keywords), axis=1)]
    else:
        filtered_df = df[df.apply(lambda row: query in str(row.values).lower(), axis=1)]

    if not filtered_df.empty:
        st.write(f"### Found {len(filtered_df)} matching projects:")
        st.dataframe(filtered_df)

        # **Check if "Company Name" Exists**
        if "Company Name" in filtered_df.columns:
            options = filtered_df["Company Name"].tolist()
            selected_projects = st.multiselect("Select up to 2 projects:", options, max_selections=2)

            if selected_projects:
                project_details = filtered_df[filtered_df["Company Name"].isin(selected_projects)]
                st.write("### Selected Projects:")
                st.dataframe(project_details)

                # **Website Crawling**
                st.write("### Extracting Website Information...")

                def extract_website_info(url):
                    try:
                        response = requests.get(url, timeout=5)
                        soup = BeautifulSoup(response.text, "html.parser")
                        return soup.title.string if soup.title else "No title found"
                    except Exception as e:
                        return f"Error fetching page: {e}"

                if "Link" in project_details.columns:
                    for _, row in project_details.iterrows():
                        project_name = row["Company Name"]
                        project_url = row["Link"]
                        website_info = extract_website_info(project_url)
                        st.write(f"**{project_name}**: {website_info}")
                else:
                    st.warning("No 'Link' column found in the dataset. Cannot extract website info.")
        else:
            st.error("Error: 'Company Name' column not found in the filtered results.")
    else:
        st.warning("No projects found matching your search.")
else:
    st.info("Enter a keyword to begin your search.")
