import pandas as pd
import streamlit as st
import requests
import re

# 🔹 Load Excel File from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")

df = load_data()

st.title("🚀 AI-Powered Project Search & Email Generator")

# 🔹 Search bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# 🔹 Filtering logic
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

# 🔹 Display Search Results
if not filtered_df.empty:
    st.write(f"### Found {len(filtered_df)} matching projects:")
    st.dataframe(filtered_df)

    # 🔹 Project Selection
    selected_projects = st.multiselect("Select up to 2 projects", filtered_df["Company Name"].tolist(), max_selections=2)

    if selected_projects:
        project_descriptions = {}

        # 🔹 GPT-Powered Website Info Extraction
        def extract_project_info_gpt(links):
            """Use GPT API to extract meaningful information from given links."""
            if not links:
                return "No valid website available."

            # Filter out app store links and split multiple links
            valid_links = [link.strip() for link in links.split() if 'http' in link and not any(re.search(pattern, link) for pattern in [r"play.google.com", r"apps.apple.com"])]

            if not valid_links:
                return "No valid website available."

            # Use GPT to extract project details
            prompt = f"Extract key information about the company and its services from these websites: {', '.join(valid_links)}"
            return "🔹 AI-Generated Summary: (This will be replaced with actual GPT output)"

        # 🔹 Process selected projects
        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            project_descriptions[company] = extract_project_info_gpt(project_info.get("Link", ""))

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Generate AI Email
        if st.button("Generate AI-Powered Email"):
            with st.spinner("Generating email..."):
                email_prompt = f"""
                Generate a professional business email for a client. The email should introduce our company, highlight these two selected projects, and explain how we can help them with similar solutions.
                
                Selected Projects:
                1. {selected_projects[0]} - {project_descriptions[selected_projects[0]]}
                2. {selected_projects[1]} - {project_descriptions[selected_projects[1]]}
                
                Format it professionally.
                """
                st.text_area("📧 AI-Generated Email", email_prompt, height=350)
