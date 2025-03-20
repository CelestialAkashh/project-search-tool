import streamlit as st
import requests
import pandas as pd
from bs4 import BeautifulSoup
import re

# 🔹 Load Excel File from GitHub
file_url = "https://github.com/CelestialAkashh/project-search-tool/raw/refs/heads/main/Copy%20of%20REAL%20Consolidated%20Project%20Portfolio.xlsx"

@st.cache_data
def load_data():
    return pd.read_excel(file_url, sheet_name="New Portfolio")

df = load_data()

st.title("🚀 AI-Powered Project Search & Email Generator")

# 🔹 Search Bar
search_query = st.text_input("Enter keywords (e.g., React Native, Fintech):")

# 🔹 Filtering Logic
filtered_df = pd.DataFrame()

if search_query:
    query = search_query.strip().lower()
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

            valid_links = [link.strip() for link in urls.split() if 'http' in link and not any(re.search(pattern, link) for pattern in [r"play.google.com", r"apps.apple.com"])]

            if not valid_links:
                return "No valid website available."

            for url in valid_links:
                try:
                    response = requests.get(url, timeout=5)
                    if response.status_code == 200:
                        soup = BeautifulSoup(response.text, "html.parser")
                        title = soup.title.text if soup.title else "No title found"
                        meta_desc = soup.find("meta", attrs={"name": "description"})
                        description = meta_desc["content"] if meta_desc else "No description available."
                        return f"{title} - {description}"
                except:
                    continue  

            return "No valid website available."

        # 🔹 Process Selected Projects
        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            with st.spinner(f"Extracting info for {company}..."):
                project_descriptions[company] = extract_project_info(project_info.get("Link", ""))

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Generate AI-Powered Email
        def generate_email(company1, desc1, company2, desc2):
            API_KEY = st.secrets["OPENROUTER_API_KEY"]
            url = "https://openrouter.ai/api/generate"
            headers = {"Authorization": f"Bearer {API_KEY}"}
            prompt = f"""
            Generate a professional email for a fintech company, highlighting past work done for {company1} and {company2}.
            - {company1}: {desc1}
            - {company2}: {desc2}
            The email should be structured, formal, and engaging.
            """

            payload = {
                "model": "deepseek-chat",
                "prompt": prompt,
                "max_tokens": 500
            }

            try:
                response = requests.post(url, headers=headers, json=payload)

                if response.status_code == 200:
                    data = response.json()
                    if "choices" in data and len(data["choices"]) > 0:
                        return data["choices"][0]["message"]["content"]
                    else:
                        return "⚠️ AI could not generate a response. Try again."
                else:
                    return f"❌ API Error {response.status_code}: {response.text}"

            except requests.exceptions.RequestException as e:
                return f"🚨 Network Error: {e}"

        # 🔹 AI Email Generation Button
        if st.button("Generate AI-Powered Email"):
            email_content = generate_email(selected_projects[0], project_descriptions[selected_projects[0]], selected_projects[1], project_descriptions[selected_projects[1]])
            st.text_area("📧 AI-Generated Email", email_content, height=350)
