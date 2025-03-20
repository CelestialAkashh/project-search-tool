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

        # 🔹 Generate **Professional** AI Email
        if st.button("Generate AI-Powered Email"):
            email_prompt = f"""
            Subject: Bringing Your Fintech Vision to Life with AI, Cloud & Scalable Tech

            Dear [Client's Name],

            I hope you’re doing well. At [Your Company Name], we specialize in helping Fintech innovators like you **build secure, scalable, and AI-driven digital solutions**. 

            We've successfully delivered solutions for industry leaders like **{selected_projects[0]}** and **{selected_projects[1]}**, tackling key challenges in financial technology.

            🔹 **Recent Work:**
            - **{selected_projects[0]}**: {project_descriptions[selected_projects[0]]}
            - **{selected_projects[1]}**: {project_descriptions[selected_projects[1]]}

            🔹 **How We Help Fintech Businesses Like Yours:**
            - **AI-Driven Automation:** Improve efficiency and decision-making with advanced AI solutions.
            - **Security & Compliance:** Build platforms with **enterprise-grade security** and **regulatory compliance**.
            - **Cloud Optimization:** Deliver **scalable, cost-efficient cloud architectures** for seamless operations.
            - **End-to-End Development:** From **UI/UX to full-stack, AI, and data solutions**, we bring your product to life.

            We work on **flexible engagement models** (hourly, monthly, or fixed-price contracts) to match your needs.

            Let’s set up a quick call to explore how we can help bring your vision to reality. Let me know a time that works for you.

            Best regards,  
            [Your Name]  
            [Your Company]  
            """

            st.text_area("📧 AI-Generated Email", email_prompt, height=350)
