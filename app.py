import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup

# -------------------------
# Load Data from GitHub
# -------------------------
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")  # Change sheet name if needed

df = load_data()

st.title("🔍 Project Search Tool")

# Show available columns
st.write("### Columns in file:", df.columns.tolist())

# -------------------------
# Search Projects
# -------------------------
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

if search_query:
    query = search_query.strip().lower()

    # Boolean Search
    if " and " in query:
        keywords = query.split(" and ")
        filtered_df = df[df.apply(lambda row: all(kw in str(row.values).lower() for kw in keywords), axis=1)]
    
    elif " or " in query:
        keywords = query.split(" or ")
        filtered_df = df[df.apply(lambda row: any(kw in str(row.values).lower() for kw in keywords), axis=1)]
    
    else:
        # Default search (single keyword)
        filtered_df = df[df.apply(lambda row: query in str(row.values).lower(), axis=1)]

    # Display results
    if not filtered_df.empty:
        st.write(f"### Found {len(filtered_df)} matching projects:")
        st.dataframe(filtered_df)

        # -------------------------
        # MEGA Step 1: Project Selection
        # -------------------------
        options = filtered_df["Project Name"].tolist()
        selected_projects = st.multiselect("Select up to two projects:", options, max_selections=2)

        if selected_projects:
            selected_df = filtered_df[filtered_df["Project Name"].isin(selected_projects)]
            st.write("### Selected Projects:")
            st.dataframe(selected_df)
            
            # -------------------------
            # MEGA Step 2: Website Crawling
            # -------------------------
            def get_project_details(url):
                try:
                    response = requests.get(url, timeout=10)
                    soup = BeautifulSoup(response.text, "html.parser")
                    p = soup.find("p")
                    return p.get_text(strip=True) if p else "No details found."
                except Exception as e:
                    return f"Error fetching details: {e}"

            if st.button("Crawl Selected Project Websites"):
                st.write("### Website Details:")
                for idx, row in selected_df.iterrows():
                    project_name = row["Project Name"]
                    project_link = row.get("Project Link", None)  # Ensure this column exists
                    if pd.notna(project_link) and project_link.startswith("http"):
                        detail = get_project_details(project_link)
                    else:
                        detail = "Invalid or missing URL."
                    
                    st.write(f"**{project_name}** - {detail}")

        else:
            st.info("Please select up to two projects.")

    else:
        st.warning("No projects found matching your search.")

else:
    st.info("Enter a keyword to begin your search.")
