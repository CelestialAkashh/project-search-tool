import pandas as pd
import streamlit as st
import requests

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
    filtered_df = df[df.apply(lambda row: query in str(row.values).lower(), axis=1)]

# 🔹 Display Search Results
if not filtered_df.empty:
    st.write(f"### Found {len(filtered_df)} matching projects:")
    st.dataframe(filtered_df)

    # 🔹 Project Selection
    selected_projects = st.multiselect("Select up to 2 projects", filtered_df["Company Name"].tolist(), max_selections=2)

    if selected_projects:
        project_descriptions = {}

        # 🔹 OpenRouter API Function (Scraping + Email)
        def get_project_info_and_email(query):
            """Fetches project-related data + generates email via OpenRouter"""
            API_KEY = st.secrets["OPENROUTER_API_KEY"]  # Use API key securely
            url = "https://openrouter.ai/api/generate"
            headers = {"Authorization": f"Bearer {API_KEY}"}
            payload = {
                "model": "deepseek-chat",  # Use free DeepSeek model
                "prompt": f"Provide detailed information about {query} for a business email.",
                "max_tokens": 500
            }

            try:
                response = requests.post(url, headers=headers, json=payload)
                if response.status_code == 200:
                    return response.json()["choices"][0]["message"]["content"]
                else:
                    return "No valid data found."
            except Exception as e:
                return f"Error: {e}"

        # 🔹 Fetch project info using OpenRouter API
        for company in selected_projects:
            project_info = filtered_df[filtered_df["Company Name"] == company].iloc[0]
            with st.spinner(f"Extracting & generating email for {company}..."):
                project_descriptions[company] = get_project_info_and_email(company)

        # 🔹 Display Extracted Info
        st.write("### Extracted Project Info:")
        for company, desc in project_descriptions.items():
            st.write(f"**{company}:** {desc}")

        # 🔹 Show AI-Generated Email
        st.text_area("📧 AI-Generated Email", project_descriptions[selected_projects[0]], height=350)
