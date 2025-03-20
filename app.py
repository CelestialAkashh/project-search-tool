import pandas as pd
import streamlit as st
import requests
from bs4 import BeautifulSoup
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

        # 🔹 Website Scraping Function
        def extract_project_info(urls):
            """Extracts website title & meta description from first valid link"""
            if not urls:
                return "No valid website available."

            # Filter valid website links (remove Play Store, App Store links)
            valid_links = [link.strip() for link in urls.split() if 'http' in link and not any(re.search(pattern, link) for pattern in [r"play.google.com", r"apps.apple.com"])]

            if not valid_links:
                return "No valid website available."

            # Try first valid website
            for url in valid_links:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        title = soup.title.text if soup.title else "No title found"
                        meta_desc = soup.find("meta", attrs={"name": "description"})
                        description = meta_desc["content"] if meta_desc else "No description available."
                        return f"**{title}** - {description}"
                except:
                    continue  # Skip if error

            return "No valid website available."

        # 🔹 Process selected projects
        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            with st.spinner(f"Extracting info for {company}..."):
                project_descriptions[company] = extract_project_info(project_info.get("Link", ""))

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Generate AI Email
        if st.button("Generate AI-Powered Email"):
            email_prompt = f"""
            Subject: Exploring Collaboration Opportunities

            Dear [Client's Name],

            I hope you're doing well! I wanted to introduce our company and discuss potential collaboration. We specialize in delivering tailored solutions, and I noticed that your company, {selected_projects[0]}, is doing some great work in the industry.

            Here are two relevant projects we have worked on:

            1. {selected_projects[0]} - {project_descriptions[selected_projects[0]]}
            2. {selected_projects[1]} - {project_descriptions[selected_projects[1]]}

            I'd love to connect and explore how we can help you with similar solutions. Let me know if you're open to a quick call.

            Best regards,  
            [Your Name]  
            [Your Company]  
            """

            st.text_area("📧 AI-Generated Email", email_prompt, height=350)
