import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup  # Make sure BeautifulSoup is installed
import requests  # Needed for website crawling

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
filtered_df = pd.DataFrame()  # Default to empty DataFrame

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
        filtered_df = df[df.apply(lambda row: query in str(row.values).lower(), axis=1)]

    # Display results
    if not filtered_df.empty:
        st.write(f"### Found {len(filtered_df)} matching projects:")
        st.dataframe(filtered_df)

        # Ensure "Company Name" column exists before using it
        if "Company Name" in filtered_df.columns:
            options = filtered_df["company Name"].tolist()
            selected_projects = st.multiselect("Select up to 2 projects:", options, max_selections=2)

            # Store selected project details
            if selected_projects:
                project_details = filtered_df[filtered_df["Company Name"].isin(selected_projects)]

                # Display selected project details
                st.write("### Selected Projects:")
                st.dataframe(project_details)

                # Next Step: Website Crawling
                st.write("### Extracting Website Information...")
                
                def extract_website_info(url):
                    try:
                        response = requests.get(url, timeout=5)
                        soup = BeautifulSoup(response.text, "html.parser")
                        return soup.title.string if soup.title else "No title found"
                    except Exception as e:
                        return f"Error fetching page: {e}"

                # Assuming project links are in a column named "Link"
                if "Link" in project_details.columns:
                    for _, row in project_details.iterrows():
                        project_name = row["Project Name"]
                        project_url = row["Link"]
                        website_info = extract_website_info(project_url)
                        st.write(f"**{project_name}**: {website_info}")
                else:
                    st.warning("No 'Link' column found in the dataset. Cannot extract website info.")
        else:
            st.error("Error: 'Project Name' column not found in the filtered results.")
    else:
        st.warning("No projects found matching your search.")
else:
    st.info("Enter a keyword to begin your search.")
