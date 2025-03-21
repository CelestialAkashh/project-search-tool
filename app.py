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

    def extract_project_info(url):
        """Scrapes the webpage title and meta description using requests & BeautifulSoup."""
        if not url or not url.startswith("http"):
            return "No valid website available."

        try:
            response = requests.get(url, timeout=10, headers={"User-Agent": "Mozilla/5.0"})
            if response.status_code != 200:
                return "Website not accessible."

            soup = BeautifulSoup(response.content, "html.parser")
            title = soup.title.string if soup.title else "No Title Found"
            meta_desc = soup.find("meta", attrs={"name": "description"})
            description = meta_desc["content"] if meta_desc else "No description available."

            return f"{title} - {description}"
        except requests.exceptions.RequestException:
            return "Error fetching website data."

    # 🔹 Process selected projects
    if selected_projects:
        project_descriptions = {}

        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            with st.spinner(f"Extracting info for {company}..."):
                project_descriptions[company] = extract_project_info(project_info.get("Link", ""))

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 OpenRouter AI Email Generation
        def generate_email(company1, desc1, company2, desc2):
            API_KEY = st.secrets["OPENROUTER_API_KEY"]
            url = "https://openrouter.ai/api/generate"

            headers = {"Authorization": f"Bearer {API_KEY}", "Content-Type": "application/json"}
            prompt = f"""
            Generate a professional email for a fintech company, highlighting past work done for {company1} and {company2}.
            - {company1}: {desc1}
            - {company2}: {desc2}
            The email should be structured, formal, and engaging.
            """

            payload = {"model": "deepseek-chat", "prompt": prompt, "max_tokens": 500}

            try:
                response = requests.post(url, headers=headers, json=payload, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    return data.get("choices", [{}])[0].get("message", {}).get("content", "⚠️ AI did not return a response.")
                return f"❌ API Error {response.status_code}: {response.text}"
            except requests.exceptions.RequestException as e:
                return f"🚨 Network Error: {e}"

        if st.button("Generate AI-Powered Email"):
            email_content = generate_email(
                selected_projects[0], project_descriptions[selected_projects[0]],
                selected_projects[1], project_descriptions[selected_projects[1]]
            )
            st.text_area("📧 AI-Generated Email", email_content, height=350)
